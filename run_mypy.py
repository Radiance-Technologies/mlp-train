"""
Pre-commit hook script that performs static type checking with `mypy`.

Unlike the official pre-commit hook, this script checks the entire
package.
"""

import os
import subprocess
from pathlib import Path

import oslex
import toml

ROOT_DIR = Path(__file__).parent

if __name__ == '__main__':
    os.chdir(ROOT_DIR)
    project_config = toml.load('pyproject.toml')
    project_name = project_config['project']['name']
    # protect against shell injection
    project_name = oslex.quote(project_name).replace('-', '_')
    subprocess.run(f'mypy --package {project_name}', shell=True, check=True)
