# mlcenter


[![PyPi](https://img.shields.io/pypi/v/mlcenter.svg)](https://pypi.python.org/pypi/mlcenter)
[![Travis](https://img.shields.io/travis/cristianexer/mlcenter.svg)](https://travis-ci.com/cristianexer/mlcenter)
[![Documentation](https://readthedocs.org/projects/mlcenter/badge/?version=latest)](https://mlcenter.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/cristianexer/mlcenter/shield.svg)](https://pyup.io/repos/github/cristianexer/mlcenter/)


Python client for MLCenter MLOps Platform (https://mlcenter.org)

## Installation

```bash
pip install mlcenter
```

## Dependencies

1. Docker/Docker Compose - [See Installation Instructions](https://docs.docker.com/compose/install/)
2. MLCenter Server - [See Installation Instructions](https://github.com/mlcenter-org/mlcenter-server)


## Usage

[See example notebook](https://github.com/mlcenter-org/mlcenter/blob/main/examples/01-Titanic.ipynb)

```python

from mlcenter import MLCenter

center = MLCenter(
    
    # These variables are optionoal, and if not provided, will be taken from the environment variables
    ####################################
    MLCENTER_URL='http://localhost:8000',
    MLCENTER_USERNAME='<username>',
    MLCENTER_PASSWORD='<password>',
    ####################################
    
    # Project ID is required and you can get the id from the project created in the MLCenter UI
    PROJECT_ID='<project_id>',
    )

```



## Developing

Run `make` for help

    make install             # Run `poetry install`
    make showdeps            # run poetry to show deps
    make lint                # Runs bandit and black in check mode
    make format              # Formats you code with Black
    make test                # run pytest with coverage
    make build               # run `poetry build` to build source distribution and wheel
    make jupyter             # run the jupyter-lab server
