#!/usr/bin/env bash
#
# NB: smoke tests are run via `make smoke-test`, 
# or equivalently, `make stest` or `tox -e stest`.
#
# NB: Unlike integration testing these tests run from github actions, 
# so without an AWS profile we can only test the CLI tool for structure and 
# not for functionality.
#
set -xeuo pipefail
python -m ssm --help
ssm --help
