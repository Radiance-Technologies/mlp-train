from __future__ import annotations

import mlptrain as mlt
import argparse
import warnings
from mlptrain.config import Config
from mlptrain.potentials import MLPotential
import os
import gc
import glob
import time
import numpy as np
import logging
from mlptrain.log import logger
import autode as ade
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ase.calculators.calculator import Calculator as ASECalculator


class MACE(MLPotential):

    def __init__(
        self,
        name: str,
        system: 'mlt.System',
        foundation: Optional[str] = None,
    ) -> None:
        """
        MACE machine learning potential

        -----------------------------------------------------------------------
        Arguments:
            name: (str) Name of the potential, used in naming output files

            system: (mlptrain.System) Object defining the system without specifying the coordinates

            foundation: (str) Either the shortcut of the foundation model used in fine-tunning
                         like "medium_off" for MACE-OFF(M), "medium" for MACE-MP-0(M), or the path to the foundation model.

                         Here, naive fine-tuning is default without any other argument specified.

                         To initiate multi-head fine-tuning, specify mace_params['pt_train']=/path/to/replay/dataset
                         For MACE-MP models, the replay dataset is provided by MACE through setting mace_params['pt_train']='mp'
                         Some Replay datasets could be accessed here: https://github.com/ACEsuit/mace-foundations/releases
                         More details on https://github.com/ACEsuit/mace/tree/main?tab=readme-ov-file#pretrained-foundation-models
        """

        super().__init__(name=name, system=system)

        import mace
        from importlib.metadata import version

        # Filter out FutureWarning from e3nn: You are using `torch.load` with `weights_only=False`...
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            import mace.tools

        self.foundation = foundation
        logger.info(f'MACE version: {version("mace-torch")}')

        mace.tools.set_seeds(Config.mace_params['seed'])
        mace.tools.set_default_dtype(str(Config.mace_params['dtype']))

    @property
    def filename(self) -> str:
        """Name of the file where potential is stored"""
        return f'{self.name}.model'

    @property
    def requires_atomic_energies(self) -> bool:
        return True

    @property
    def requires_non_zero_box_size(self) -> bool:
        """MACE cannot use a zero size box"""
        return True

    @property
    def get_E0s(self):
        E0s_dictionary = {}
        atomic_energies = self.atomic_energies
        for key, value in atomic_energies.items():
            Atom = ade.Atom(atomic_symbol=key)
            atomic_number = Atom.atomic_number
            E0s_dictionary[atomic_number] = float(value)
        return E0s_dictionary

    @property
    def valid_fraction(self) -> float:
        """Fraction of the whole dataset to be used as validation set"""
        valid_fraction = Config.mace_params['valid_fraction']
        if not isinstance(valid_fraction, float):
            raise ValueError(
                f"Invalid parameter valid_fraction '{valid_fraction}'")

        _min_dataset = -(1 // -valid_fraction)

        if self.n_train == 1:
            raise ValueError(
                'MACE training requires at least 2 configurations')
        elif self.n_train >= _min_dataset:
            return valid_fraction
        else:
            # Valid fraction which sets at least 1 datapoint for validation
            _unrounded_valid_fraction = 1 / self.n_train
            return -((_unrounded_valid_fraction * 100) // -1) / 100

    @property
    def batch_size(self) -> int:
        """Batch size of the training set"""
        batch_size = Config.mace_params['batch_size']
        if not isinstance(batch_size, int):
            raise ValueError(f"Invalid parameter batch_size '{batch_size}'")

        if self.n_train * (1 - self.valid_fraction) < batch_size:
            return int(np.floor(self.n_train * (1 - self.valid_fraction)))
        else:
            return batch_size

    @property
    def args(self) -> 'argparse.Namespace':
        """Namespace containing default and custom MACE parameters"""
        import mace.tools
        import json

        cli_dict = {
            'name': self.name,
            'train_file': f'{self.name}_data.xyz',
            'scaling': 'rms_forces_scaling',
            'batch_size': self.batch_size,
            'valid_batch_size': self.batch_size,
            'energy_key': 'energy',
            'forces_key': 'forces',
            'default_dtype': str(Config.mace_params['dtype']),
            'enable_cueq': str(Config.mace_params['cueq']),
            'E0s': self.get_E0s,
        }

        if getattr(self, 'foundation', None) is not None:
            cli_dict['foundation_model'] = str(self.foundation)
            pt_train = Config.mace_params.get('pt_train')

            if pt_train is not None:
                if not isinstance(pt_train, str) or not pt_train.strip():
                    raise ValueError(
                        'pt_train must be a non-empty path string.')
                if pt_train != 'mp' and not os.path.exists(pt_train):
                    raise FileNotFoundError(
                        f'pt_train path does not exist: {pt_train}')

                cli_dict['pt_train_file'] = pt_train
                cli_dict['multiheads_finetuning'] = True
                logger.info('Multihead fine-tuning launched')

            else:
                cli_dict['multiheads_finetuning'] = False
                logger.info(
                    'Naive fine-tuning launched since no pt_train provided.')

        valid_file = Config.mace_params.get('valid_file')
        if valid_file is not None:
            if not isinstance(valid_file, str) or not valid_file.strip():
                raise ValueError('valid_file must be a non-empty path string.')
            if not os.path.exists(valid_file):
                raise FileNotFoundError(
                    f'valid_file path does not exist: {valid_file}')
            cli_dict['valid_file'] = valid_file
            logger.info(f'Using structures in {valid_file} as validation set')
        else:
            cli_dict['valid_fraction'] = self.valid_fraction

        for key, value in Config.mace_params.items():
            if key not in cli_dict and key not in ('pt_train', 'valid_file',
                                                   'dtype', 'cueq',
                                                   'calc_device'):
                cli_dict[key] = value

        parser = mace.tools.build_default_arg_parser()
        args_list = []

        for key, value in cli_dict.items():
            if value is None:
                continue

            flag = f'--{key}'
            action = parser._option_string_actions.get(flag)

            if isinstance(action, argparse._StoreTrueAction):
                if value:
                    args_list.append(flag)
            elif isinstance(value, dict):
                args_list.extend([flag, json.dumps(value)])
            else:
                args_list.extend([flag, str(value)])

        return parser.parse_args(args_list)

    @property
    def ase_calculator(self) -> ASECalculator:
        """ASE calculator for MACE potential"""
        from mace.calculators import MACECalculator

        calculator = MACECalculator(
            model_paths=self.filename,
            device=str(Config.mace_params['calc_device']),
            enable_cueq=Config.mace_params['cueq'],
        )
        return calculator

    def _train(self, n_cores: Optional[int] = None) -> None:
        """
        Train a MACE potential using the data as .xyz file and save the
        final potential as .model file

        -----------------------------------------------------------------------
        Arguments:

            n_cores: (int) Number of cores to use in training
        """
        import torch
        from mace.cli.run_train import run as train_mace

        def remove_root_logging_handlers() -> list[logging.Handler]:
            """Remove and return root logging handlers before calling MACE"""

            # Remove existing logging as MACE creates it's own loggers
            root_logger = logging.getLogger()
            root_logging_handlers = list(root_logger.handlers)
            for handler in root_logging_handlers:
                root_logger.removeHandler(handler)
            return root_logging_handlers

        n_cores = n_cores if n_cores is not None else Config.n_cores
        os.environ['OMP_NUM_THREADS'] = str(n_cores)
        logger.info('Training a MACE potential on '
                    f'*{len(self.training_data)}* training data, '
                    f'using {n_cores} cores for training.')

        for config in self.training_data:
            if self.requires_non_zero_box_size and config.box is None:
                config.box = mlt.Box([100, 100, 100])

        self.training_data.save_xyz(filename=f'{self.name}_data.xyz')

        start_time = time.perf_counter()

        # Remove mlp-train root logging handlers, but save for later
        our_logging_handlers = remove_root_logging_handlers()

        try:
            train_mace(self.args)
        finally:
            # Remove MACE root logging handlers and restore pre-existing ones.
            remove_root_logging_handlers()
            root_logger = logging.getLogger()
            for handler in our_logging_handlers:
                root_logger.addHandler(handler)

        delta_time = time.perf_counter() - start_time

        logger.info(f'MACE training ran in {delta_time / 60:.1f} m.')

        os.remove(f'{self.name}_data.xyz')

        gc.collect()
        torch.cuda.empty_cache()

        for file in glob.glob('./checkpoints/*.pt'):
            os.remove(file)

        return None
