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
ssm put /tests/integration/ssm-tool/key1 value1
ssm ls /tests/integration/ssm-tool/
ssm ls /tests/
ssm ls /tests/ --format json | jq .
ssm ls /tests/ --format yaml
ssm ls /tests/integration/ssm-tool --dirs-only
ssm ls-dirs /tests/integration/ssm-tool 
ssm copy /tests/integration/ssm-tool/key1 /tests/integration/ssm-tool/key2
ssm stat /tests/ --format json | jq .
ssm stat /tests/ --format json | jq .parameters.count
ssm stat /tests/ --format json --caller-context | jq .context
ssm get /tests/integration/ssm-tool/key1
ssm get-many /tests/integration/ssm-tool/ --format stdout
ssm get-many /tests/integration/ssm-tool/ --flat-output --format yaml
ssm rm /tests/integration/ssm-tool/key1
ssm rm /tests/integration/ssm-tool/key2
rm -f .tmp.*