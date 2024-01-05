""" ssm.api

  See the docs here:
    https://github.com/Robot-Wranglers/aws-ssm-tool
"""

import json
import collections

import yaml

from ssm import util
from ssm.api.environment import Environment

LOGGER = util.get_logger(__name__)


def _get_env(env=None, **kwargs):
    """ """
    env = Environment.from_profile(env) if util.is_string(env) else env
    env.logger.info("getting client")
    assert env
    return env


def _get_handle(**kwargs):
    """ """
    return _get_env(**kwargs).secrets


def read(secret_name, **kwargs):
    """
    get a secret
    """
    assert secret_name, f"cannot read secret_name `{secret_name}`"
    secrets = _get_handle(**kwargs)
    try:
        return secrets[secret_name]
    except KeyError as exc:
        LOGGER.error(f"KeyError: {exc}")
        raise SystemExit(1)


def stat(path="/", format="stdout", **kwargs):
    """
    reports status, including account details and metadata summary for SSM parameters.
    """
    env = _get_env(**kwargs)
    caller_id = env.caller_id
    result = collections.OrderedDict()
    result.update(
        context=dict(
            user=dict(
                id=caller_id.get("UserId"),
                arn=caller_id.get("Arn"),
            ),
            account=dict(
                profile_name=env.profile_name,
                id=env.account_id,
                alias=env.account_alias,
                region_name=env.region_name,
            ),
        )
    )
    result.update(parameters=dict(root=path, count=len(env.secrets.under("/"))))
    return result
    


def list(secret_name, **kwargs):
    """
    list parameters with prefixes below the given path
    """
    # WARNING: do not use `list()` here..
    secrets = _get_handle(**kwargs)
    result = secrets.under(secret_name).keys()
    result = [x for x in result]
    return result


def get_many(namespace, **kwargs):
    """
    get many secrets from hierarchy/namespace
    """
    assert format, "output format is required"
    secrets = _get_handle(**kwargs)
    result = secrets.under(namespace)
    return result 

def delete(secret_name, no_backup=False, **kwargs):
    """delete secret (keeping a local-backup is default)"""

    def get_backup_file(prefix):
        return ".tmp.{}".format(prefix.replace("/", "_"))

    secrets = _get_handle(**kwargs)
    parameter = read(secret_name=secret_name, **kwargs)
    if not no_backup:
        backup = get_backup_file(secret_name)
        LOGGER.debug(f"backup to: {backup}")
        with open(backup, "w") as fhandle:
            fhandle.write(parameter)
        del secrets[secret_name]
        return parameter


def move(src_name, dest_name, src_env=None, dest_env=None, **kwargs):
    """move a secret"""
    result = copy(src_name, dest_name, src_env=src_env, dest_env=dest_env, **kwargs)
    src_env = Environment.from_profile(src_env)
    del src_env.secrets[src_name]
    return result


def move_many(src_name, dest_name, **kwargs):
    """
    move a whole path of secrets
    """
    dest_name = dest_name[:-1] if dest_name.endswith("/") else dest_name
    secrets = _get_handle(**kwargs)
    names = secrets.under(src_name).keys()
    plan, results = [], []
    for name in names:
        leaf = name[len(src_name) :]
        leaf = leaf[:-1] if leaf.endswith("/") else leaf
        leaf = leaf[1:] if leaf.startswith("/") else leaf
        args = (name, "/".join([dest_name, leaf]))
        LOGGER.debug(f"mv {args} {kwargs}")
        plan.append([args, kwargs])
    LOGGER.warning(f"plan:\n{plan}")
    for args, kwargs in plan:
        results.append(move(*args, **kwargs))
    return results


def copy(src_name, dest_name, src_env=None, dest_env=None, **kwargs):
    """copy a secret"""
    # NB: mind the signature, this code is reused by `move`
    src_env = _get_handle(env=src_env)
    dest_env = _get_handle(env=dest_env)
    dest_name = dest_name or src_name
    value = src_env[src_name]
    dest_env[dest_name] = value
    return True

def update(secret_name, value, file=None, **kwargs):
    """
    put a secret
    """
    if all([not value, not file]):
        err = (
            "when `value` is not given as second arg, "
            "then `input_file` must be provided"
        )
        LOGGER.critical(err)
        raise RuntimeError(err)
    value = value or open(file).read()
    secrets = _get_handle(**kwargs)
    secrets[secret_name] = value
    return True


def put_many(secret_name, input_file=None, **kwargs):  # noqa
    """ put many secrets """
    raise NotImplementedError()
