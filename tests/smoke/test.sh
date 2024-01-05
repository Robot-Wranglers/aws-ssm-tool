#!/usr/bin/env bash
#
# NB: smoke tests are run via `make smoke-test`, 
# or equivalently, `make stest` or `tox -e stest`.
#
set -xeuo pipefail
python -m ssm --help
ssm --help
ssm stat --format json | jq .
ssm stat --format json | jq .parameters.count
ssm ls /
ssm ls / --format json | jq .
ssm ls / --format yaml
ssm ls /