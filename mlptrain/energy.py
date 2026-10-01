from typing import Optional


class Energy:
    """Energy in units of eV"""

    def __init__(
        self,
        predicted: Optional[float] = None,
        true: Optional[float] = None,
        bias: Optional[float] = None,
        inherited_bias: Optional[float] = None,
        variance: Optional[float] = None,
        aleatoric_uncertainty: Optional[float] = None,
        epistemic_uncertainty: Optional[float] = None,
    ):
        """
        Energy

        -----------------------------------------------------------------------
        Arguments:
            predicted:
            true:
            bias:
            inherited_bias:
            variance:
            aleatoric_uncertainty:
            epistemic_uncertainty:
        """

        self.predicted = predicted
        self.true = true
        self.bias = bias
        self.inherited_bias = inherited_bias
        self.variance = variance
        self.aleatoric_uncertainty = aleatoric_uncertainty
        self.epistemic_uncertainty = epistemic_uncertainty

    @property
    def delta(self) -> float:
        """
        Difference between true and predicted energies

        -----------------------------------------------------------------------
        Returns:
            (float):  E_true - E_predicted

        Raises:
            (ValueError): If at least one energy is not defined
        """

        if self.true is None:
            raise ValueError('Cannot calculate ∆E. No true energy')

        if self.predicted is None:
            raise ValueError('Cannot calculate ∆E. No predicted energy')

        return self.true - self.predicted
