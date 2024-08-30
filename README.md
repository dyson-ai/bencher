# python_template
A template repo for python projects that is set up using [pixi](https://pixi.sh). 

This has basic setup for

* pylint
* ruff
* black
* pytest
* codecov
* git-lfs
* basic github actions ci
* pulling updates from this template


## Continuous Integration Status

[![Ci](https://github.com/blooop/python_template/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/blooop/python_template/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://codecov.io/gh/blooop/python_template/branch/main/graph/badge.svg?token=Y212GW1PG6)](https://codecov.io/gh/blooop/python_template)
[![GitHub issues](https://img.shields.io/github/issues/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/issues/)
[![GitHub pull-requests merged](https://badgen.net/github/merged-prs/blooop/python_template)](https://github.com/blooop/python_template/pulls?q=is%3Amerged)
[![GitHub release](https://img.shields.io/github/release/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/releases/)
[![License](https://img.shields.io/pypi/l/bencher)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh)


# Install

There are two methods of using this project.  

1. Use github to use this project as a template
2. Clone the project and run, `scripts/update_from_template.sh` and then run the "rename project" task to rename the project.

If you want to use docker you may want to run the `scripts/setup_host.sh` script.  It will set up docker and nvidia-docker (assuming you are on ubuntu22.04).

If you are using pixi, you can either follow the instructions on the pixi [website](https://prefix.dev/) or run `scripts/install_pixi.sh`


# Usage

There are currently two ways of running code.  The legacy docker way and the work in progress pixi way. 

## Legacy

run the `scripts/launch_vscode.sh` script to build and connect to a docker container.  The docker container is dynamically generated using [rocker](https://github.com/osrf/rocker) and [deps rocker](https://github.com/blooop/deps_rocker).  [deps rocker](https://github.com/blooop/deps_rocker) looks at the python_template.deps.yaml file to install any required apt, pip or shell scripts and launches a container that vscode attaches to. 

## Pixi

If you have pixi installed on your host machine you can run any of the tasks defined in pyproject.toml.  The legacy method also installs pixi in the container so you have access to pixi there. 

The main pixi tasks are related to ci.  Github actions runs the pixi task "ci".  The ci is mostly likey to fail from a lockfile mismatch.  Use the "fix" task to fix any lockfile related problems. 

## vscode tasks

There are two core tasks.  

1. set \<cfg\> from active file

    This sets \<cfg\> to the currently opened file in the editor

2. run \<cfg\>

    This runs python with the file set in \<cfg\>



