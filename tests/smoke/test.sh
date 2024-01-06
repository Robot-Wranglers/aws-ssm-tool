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
ssm put /tests/integration/ssm-tool/key1 value1
ssm copy /tests/integration/ssm-tool/key1 /tests/integration/ssm-tool/key2
ssm get /tests/integration/ssm-tool/key1
ssm get-many /tests/integration/ssm-tool/ --format stdout
ssm get-many /tests/integration/ssm-tool/ --flat-output --format yaml