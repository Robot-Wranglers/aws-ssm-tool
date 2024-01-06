#!/usr/bin/env bash
#
# NB: integration tests are run via `make integration-test`, 
# or equivalently, `make itest` or `tox -e itest`.
#
# NB: unlike smoke-tests, these integration tests do NOT run 
# from github actions.  you can put tests here that require a profile
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
ssm rm /tests/integration/ssm-tool/key1
ssm rm /tests/integration/ssm-tool/key2