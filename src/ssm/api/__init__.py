""" ssm.api

  See the docs here:
    https://github.com/Robot-Wranglers/aws-ssm-tool
"""

import collections

import botocore

from ssm import util
from ssm.api.environment import Environment

LOGGER = util.get_logger(__name__)


def _get_env(profile=None, env=None, **kwargs):
    """gets environment from environment or named profile"""
    assert profile or env, str(kwargs)
    env = Environment.from_profile(profile) if profile else env
    assert env
    return env


def _get_client(**kwargs):
    """gets handle for the secrets-manager"""
    env = _get_env(**kwargs)
    env.logger.info("getting client")
    sman = env.secrets
    return sman


def read(secret_name, **kwargs):
    """
    reads a secret
    """
    assert secret_name, f"cannot read secret_name `{secret_name}`"
    secrets = _get_client(**kwargs)
    try:
        return secrets[secret_name]
    except KeyError as exc:
        LOGGER.error(f"KeyError: {exc}")
        raise SystemExit(1)


def stat(path_prefix="/", caller_context: bool = True, **kwargs):
    """
    reports status, including account details and metadata summary for SSM parameters.
    """
    env = _get_env(**kwargs)
    caller_id = env.caller_id
    result = collections.OrderedDict()
    if caller_context:
        LOGGER.info("lookup caller-context")
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
    result.update(
        parameters=dict(
            root=path_prefix,
            key_count=len(env.secrets.under(path_prefix)),
            children=env.secrets.children(path_prefix),
        ),
    )
    return result


import typing


def list_dirs(path_prefix, **kwargs) -> typing.List:
    """
    lists subpaths (i.e. directories) under the given path.
    no leaf nodes are returned
    """
    kwargs.update(dirs_only=True)
    return list(path_prefix, **kwargs)


def list(path_prefix, dirs_only: bool = False, **kwargs) -> typing.List:
    """
    Lists parameters with prefixes below the given path.

    This is recursive by default and only returns leafs:
    use `list-dirs` or pass `--dirs` to get directories only.
    """
    # WARNING: do not use `list()` builtin here..
    secrets = _get_client(**kwargs)
    if dirs_only:
        return secrets.children(path_prefix)
    result = secrets.under(path_prefix).keys()
    result = [x for x in result]
    return result


def get_many(namespace, flat_output: bool = False, **kwargs):
    """
    gets many secrets from specified hierarchy/namespace
    """
    secrets = _get_client(**kwargs)
    result = secrets.under(namespace)
    if flat_output:
        result = util.flatten_output(result)
    return result


def delete(secret_name, no_backup=False, **kwargs):
    """deletes secret (keeping a local-backup is default)"""

    def get_backup_file(prefix):
        return ".tmp.{}".format(prefix.replace("/", "_"))

    secrets = _get_client(**kwargs)
    try:
        parameter = read(secret_name=secret_name, **kwargs)
    except (botocore.exceptions.ClientError,) as exc:
        LOGGER.warning(f"error reading secret @ `{secret_name}` (is this a path?)")
        parameter = None
    if parameter is not None:
        if not no_backup:
            backup = get_backup_file(secret_name)
            LOGGER.debug(f"backup to: {backup}")
            with open(backup, "w") as fhandle:
                fhandle.write(parameter)
        del secrets[secret_name]
        return parameter
    else:
        return False


def move(
    src_name,
    dst_name,
    src_profile: str = "default",
    dst_profile: str = "default",
    **kwargs,
):
    """
    moves a secret from src to dest
    """
    result = copy(
        src_name, dst_name, src_profile=src_profile, dst_profile=dst_profile, **kwargs
    )
    if result:
        src_profile = Environment.from_profile(src_profile)
        del src_profile.secrets[src_name]
    return result


def move_many(
    src_name,
    dst_name,
    src_profile: str = "default",
    dst_profile: str = "default",
    **kwargs,
):
    """
    moves a whole path of secrets to a new location
    """
    dst_name = dst_name[:-1] if dst_name.endswith("/") else dst_name
    src_man = _get_client(profile=src_profile)
    names = [n for n in src_man.under(src_name).keys()]
    LOGGER.debug(f"moving {len(names)} parameters under `{src_name}`")
    results = []
    for name in names:
        new_name = "/".join([dst_name, name[len(src_name) :]])
        LOGGER.debug(f"  {name} -> {new_name}")
        results.append(
            move(
                name,
                new_name,
                src_profile=src_profile,
                dst_profile=dst_profile,
                **kwargs,
            )
        )
    return results


def copy(
    src_name,
    dst_name,
    src_profile: str = "default",
    dst_profile: str = "default",
    **kwargs,
):
    """
    copies a secret from given source to destination
    """
    # NB: mind the signature, this code is reused by `move`
    src_man = _get_client(profile=src_profile)
    dst_man = _get_client(profile=dst_profile)
    dst_name = dst_name or src_name
    try:
        value = src_man[src_name]
    except (botocore.exceptions.ClientError, KeyError) as exc:
        LOGGER.error(f"Cant retrieve `{src_name}` using profile `{src_man.env.name}`!")
        LOGGER.warning(f"Hint: Use `ssm copy-many ...` if `{src_name}` is a hierarchy")
        return False
    else:
        dst_man[dst_name] = value
        return True


def update(secret_name, value, file=None, **kwargs):
    """
    updates secret in given location with new value
    """
    if all([not value, not file]):
        err = (
            "when `value` is not given as second arg, "
            "then `input_file` must be provided"
        )
        LOGGER.critical(err)
        raise RuntimeError(err)
    value = value or open(file).read()
    secrets = _get_client(**kwargs)
    secrets[secret_name] = value
    return True


def delete_path(path_prefix, **kwargs):
    """ """
    raise NotImplementedError()


def put_many(secret_name, input_file=None, **kwargs):  # noqa
    """
    put many secrets
    """
    raise NotImplementedError()
