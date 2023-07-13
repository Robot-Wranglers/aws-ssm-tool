""" ssm.api

See the docs here:
  https://github.com/elo-enterprises/aws-secrets
"""

import json

import yaml

from ssm import util  # chatops, keybase

from .environment import Environment

LOGGER = util.get_logger(__name__)


# @util.memoized
def _get_handle(env=None, **kwargs):
    """ """
    assert env
    env = Environment.from_profile(env) if util.is_string(env) else env
    env.logger.info("this environment will be used for retrieving secrets")
    return env.secrets


def read(secret_name, **kwargs):
    """
    get a secret
    """
    assert secret_name, f"cannot read secret_name `{secret_name}`"
    secrets = _get_handle(**kwargs)

    # print(value,  file=sys.stdout)
    try:
        return secrets[secret_name]
    except KeyError as exc:
        LOGGER.error(f"KeyError: {exc}")
        raise SystemExit(1)


def list(secret_name, format="stdout", **kwargs):
    """
    list prefixes below the given path
    """
    secrets = _get_handle(**kwargs)
    return "\n".join(secrets.under(secret_name).keys())


def get_many(namespace, format="python", **kwargs):
    """
    get many secrets from hierarchy/namespace
    """
    assert format, "output format is required"
    secrets = _get_handle(**kwargs)
    result = secrets.under(namespace)
    if format in ["python"]:
        return result
    if format in ["yaml", "yml"]:
        return yaml.dump(result)
    elif format in ["json"]:
        return json.dumps(result)
    elif format in ["env"]:
        return "\n".join(["=".join([k.split("/")[-1], v]) for k, v in result.items()])
    else:
        raise RuntimeError(f"unrecognized output format `{format}`")


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
    """put many secrets"""
    raise NotImplementedError()
