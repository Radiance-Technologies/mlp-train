include Makefile.include

export

SHELL := /bin/bash

.PHONY: install test dev clean env_clean

install:
	pixi install

test:
	pixi run -e test pytest --pyargs --cov=mlptrain

dev:
	pixi run -e dev pre-commit install

clean:
	rm -rf build
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

env_clean: clean
	@echo "Removing Pixi environments (.pixi directory)..."
	rm -rf .pixi
	rm -rf pixi.lock
