""" ssm.api

  Comprehensive AWS SSM Parameter Store API.
  See the docs here: https://github.com/Robot-Wranglers/aws-ssm-tool
"""

import base64
import collections
import datetime
import fnmatch
import gzip
import hashlib
import json
import os
import re
import secrets as secrets_module
import string
import subprocess
import sys
import tarfile
import tempfile
import time
import typing

import botocore
import yaml

from ssm import util
from ssm.api.environment import Environment

LOGGER = util.get_logger(__name__)

__all__ = [
    # Core CRUD
    "read",
    "update",
    "delete",
    "delete_path",
    "list",
    "list_dirs",
    # Copy/Move
    "copy",
    "move",
    "copy_many",
    "move_many",
    "rename",
    # Bulk operations
    "get_many",
    "put_many",
    # Query/Search
    "stat",
    "search",
    "grep",
    "count",
    "tree",
    "diff",
    # History/Versioning
    "history",
    # Tags
    "tags",
    "add_tags",
    "remove_tags",
    # Sync/Backup
    "sync_pull",
    "sync_push",
    "sync_diff",
    "backup",
    "restore",
    # Environment export
    "env_export",
    # Policies
    "get_policy",
    "set_policy",
    # Watch
    "watch",
    # Templates
    "put_template",
    # Validation
    "validate",
    "lint",
    # Audit
    "audit",
    # Rotation
    "rotate",
    "generate_secret",
    # KMS
    "rekey",
    "list_by_kms",
    # CI/CD
    "inject",
    "verify_access",
    # Terraform
    "export_terraform",
    # Kubernetes
    "k8s_export",
]


# =============================================================================
# Internal Helpers
# =============================================================================


def _get_env(
    profile: typing.Optional[str] = None,
    env=None,
    role_arn: typing.Optional[str] = None,
    **kwargs,
) -> Environment:
    """Gets environment from environment or named profile."""
    if role_arn:
        return Environment.from_role(role_arn, base_profile=profile)
    if profile:
        return Environment.from_profile(profile)
    if env:
        return env
    return Environment.from_profile("default")


def _get_client(profile: typing.Optional[str] = None, **kwargs):
    """Gets handle for the secrets-manager."""
    env = _get_env(profile=profile, **kwargs)
    env.logger.info("getting client")
    return env.secrets


def _load_config() -> dict:
    """Load project configuration from .ssm.yaml if present."""
    config_paths = [".ssm.yaml", ".ssm.yml", ".ssm.json"]
    for path in config_paths:
        if os.path.exists(path):
            with open(path) as f:
                if path.endswith(".json"):
                    return json.load(f)
                return yaml.safe_load(f) or {}
    return {}


# =============================================================================
# Core CRUD Operations
# =============================================================================


def read(
    secret_name: str,
    version: typing.Optional[int] = None,
    **kwargs,
) -> str:
    """
    Reads a secret, optionally at a specific version.
    """
    assert secret_name, f"cannot read secret_name `{secret_name}`"
    env = _get_env(**kwargs)
    try:
        if version:
            params = dict(Name=f"{secret_name}:{version}", WithDecryption=True)
            return env.ssm.get_parameter(**params)["Parameter"]["Value"]
        return env.secrets[secret_name]
    except KeyError as exc:
        LOGGER.error(f"KeyError: {exc}")
        raise SystemExit(1)
    except botocore.exceptions.ClientError as exc:
        LOGGER.error(f"ClientError: {exc}")
        raise SystemExit(1)


def update(
    secret_name: str,
    value: str = "",
    file: typing.Optional[str] = None,
    stdin: bool = False,
    param_type: str = "SecureString",
    description: typing.Optional[str] = None,
    kms_key: typing.Optional[str] = None,
    tags: typing.Optional[typing.List[typing.Tuple[str, str]]] = None,
    **kwargs,
) -> bool:
    """
    Updates secret in given location with new value.
    Supports reading from file (--file), stdin (--stdin or value of '-'),
    parameter type selection (--type), and optional tags.
    """
    # Handle stdin input
    if stdin or value == "-":
        value = sys.stdin.read().strip()
    elif file:
        with open(file) as f:
            value = f.read()

    if not value:
        err = (
            "when `value` is not given as second arg, "
            "then `--file` or `--stdin` must be provided"
        )
        LOGGER.critical(err)
        raise RuntimeError(err)

    secrets = _get_client(**kwargs)
    secrets.set_secret(
        name=secret_name,
        value=value,
        param_type=param_type,
        description=description,
        kms_id=kms_key,
    )

    # Add tags if provided
    if tags:
        add_tags(secret_name, tags, **kwargs)

    return True


def delete(
    secret_name: str,
    no_backup: bool = False,
    dry_run: bool = False,
    **kwargs,
) -> typing.Union[str, bool]:
    """Deletes secret (keeping a local-backup is default). Use --dry-run to preview."""

    def get_backup_file(prefix):
        return ".tmp.{}".format(prefix.replace("/", "_"))

    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would delete: {secret_name}")
        return secret_name

    secrets = _get_client(**kwargs)
    try:
        parameter = read(secret_name=secret_name, **kwargs)
    except (botocore.exceptions.ClientError, SystemExit):
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


def delete_path(
    path_prefix: str,
    no_backup: bool = False,
    dry_run: bool = False,
    force: bool = False,
    **kwargs,
) -> typing.List[str]:
    """
    Delete all parameters under a path prefix.
    Use --dry-run to preview, --force to skip confirmation.
    """
    secrets = _get_client(**kwargs)
    keys = [k for k in secrets.under(path_prefix).keys()]

    if not keys:
        LOGGER.warning(f"No parameters found under {path_prefix}")
        return []

    if dry_run:
        LOGGER.info(
            f"[DRY-RUN] Would delete {len(keys)} parameters under {path_prefix}:"
        )
        for k in keys:
            LOGGER.info(f"  - {k}")
        return keys

    if not force:
        LOGGER.warning(f"About to delete {len(keys)} parameters under {path_prefix}")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            LOGGER.info("Aborted.")
            return []

    results = []
    for key in keys:
        result = delete(key, no_backup=no_backup, **kwargs)
        if result:
            results.append(key)
            LOGGER.info(f"Deleted: {key}")

    return results


# =============================================================================
# List Operations
# =============================================================================


def list_dirs(path_prefix: str, **kwargs) -> typing.List[str]:
    """
    Lists subpaths (i.e. directories) under the given path.
    No leaf nodes are returned.
    """
    kwargs.update(dirs_only=True)
    return list(path_prefix, **kwargs)


def list(
    path_prefix: str,
    dirs_only: bool = False,
    **kwargs,
) -> typing.List[str]:
    """
    Lists parameters with prefixes below the given path.
    This is recursive by default and only returns leafs:
    use `list-dirs` or pass `--dirs` to get directories only.
    """
    secrets = _get_client(**kwargs)
    if dirs_only:
        return secrets.children(path_prefix)
    result = secrets.under(path_prefix).keys()
    return [x for x in result]


def stat(
    path_prefix: str = "/",
    caller_context: bool = True,
    **kwargs,
) -> typing.OrderedDict:
    """
    Reports status, including account details and metadata summary for SSM parameters.
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


# =============================================================================
# Copy/Move Operations
# =============================================================================


def copy(
    src_name: str,
    dst_name: str,
    src_profile: str = "default",
    dst_profile: str = "default",
    dry_run: bool = False,
    **kwargs,
) -> bool:
    """
    Copies a secret from given source to destination. Use --dry-run to preview.
    """
    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would copy: {src_name} -> {dst_name}")
        return True

    src_man = _get_client(profile=src_profile)
    dst_man = _get_client(profile=dst_profile)
    dst_name = dst_name or src_name
    try:
        value = src_man[src_name]
    except (botocore.exceptions.ClientError, KeyError):
        LOGGER.error(f"Cant retrieve `{src_name}` using profile `{src_man.env.name}`!")
        LOGGER.warning(f"Hint: Use `ssm copy-many ...` if `{src_name}` is a hierarchy")
        return False
    else:
        dst_man[dst_name] = value
        return True


def copy_many(
    src_name: str,
    dst_name: str,
    src_profile: str = "default",
    dst_profile: str = "default",
    dry_run: bool = False,
    **kwargs,
) -> typing.List[typing.Tuple[str, str]]:
    """
    Copy all parameters from one path to another.
    Supports cross-profile copying. Use --dry-run to preview.
    """
    dst_name = dst_name.rstrip("/")
    src_name_stripped = src_name.rstrip("/")
    src_man = _get_client(profile=src_profile)
    dst_man = _get_client(profile=dst_profile)

    params = src_man.under(src_name)

    if not params:
        LOGGER.warning(f"No parameters found under {src_name}")
        return []

    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would copy {len(params)} parameters:")
        for name in params.keys():
            new_name = f"{dst_name}{name[len(src_name_stripped):]}"
            LOGGER.info(f"  {name} -> {new_name}")
        return [(k, f"{dst_name}{k[len(src_name_stripped):]}") for k in params.keys()]

    results = []
    for name, value in params.items():
        new_name = f"{dst_name}{name[len(src_name_stripped):]}"
        dst_man[new_name] = value
        results.append((name, new_name))
        LOGGER.info(f"Copied: {name} -> {new_name}")

    return results


def move(
    src_name: str,
    dst_name: str,
    src_profile: str = "default",
    dst_profile: str = "default",
    dry_run: bool = False,
    **kwargs,
) -> bool:
    """
    Moves a secret from src to dest. Use --dry-run to preview.
    """
    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would move: {src_name} -> {dst_name}")
        return True

    result = copy(
        src_name,
        dst_name,
        src_profile=src_profile,
        dst_profile=dst_profile,
        **kwargs,
    )
    if result:
        src_env = Environment.from_profile(src_profile)
        del src_env.secrets[src_name]
    return result


def move_many(
    src_name: str,
    dst_name: str,
    src_profile: str = "default",
    dst_profile: str = "default",
    dry_run: bool = False,
    **kwargs,
) -> typing.List[bool]:
    """
    Moves a whole path of secrets to a new location. Use --dry-run to preview.
    """
    dst_name = dst_name[:-1] if dst_name.endswith("/") else dst_name
    src_man = _get_client(profile=src_profile)
    names = [n for n in src_man.under(src_name).keys()]

    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would move {len(names)} parameters under `{src_name}`:")
        for name in names:
            new_name = "/".join([dst_name, name[len(src_name) :]])
            LOGGER.info(f"  {name} -> {new_name}")
        return [True] * len(names)

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


def rename(
    old_name: str,
    new_name: str,
    dry_run: bool = False,
    **kwargs,
) -> bool:
    """
    Rename a parameter (atomic copy + delete within same profile).
    """
    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would rename: {old_name} -> {new_name}")
        return True

    profile = kwargs.get("profile", "default")
    result = copy(old_name, new_name, src_profile=profile, dst_profile=profile)
    if result:
        secrets = _get_client(**kwargs)
        del secrets[old_name]
        LOGGER.info(f"Renamed: {old_name} -> {new_name}")
    return result


# =============================================================================
# Bulk Operations
# =============================================================================


def get_many(
    namespace: str,
    flat_output: bool = False,
    **kwargs,
) -> typing.Dict[str, str]:
    """
    Gets many secrets from specified hierarchy/namespace.
    """
    secrets = _get_client(**kwargs)
    result = secrets.under(namespace)
    if flat_output:
        result = util.flatten_output(result)
    return result


def put_many(
    namespace: str,
    input_file: typing.Optional[str] = None,
    format: str = "yaml",
    dry_run: bool = False,
    param_type: str = "SecureString",
    **kwargs,
) -> typing.List[str]:
    """
    Put multiple secrets from a file to a namespace.
    Expects a flat key-value structure in the input file.
    Use --dry-run to preview.
    """
    if not input_file:
        err = "input_file is required for put_many (use --file)"
        LOGGER.critical(err)
        raise RuntimeError(err)

    with open(input_file) as f:
        if format in ["yaml", "yml"]:
            data = yaml.safe_load(f)
        elif format == "json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in file, got {type(data)}")

    namespace = namespace.rstrip("/")

    if dry_run:
        LOGGER.info(
            f"[DRY-RUN] Would create {len(data)} parameters under {namespace}:"
        )
        for key in data.keys():
            LOGGER.info(f"  - {namespace}/{key}")
        return [f"{namespace}/{k}" for k in data.keys()]

    secrets = _get_client(**kwargs)
    results = []
    for key, value in data.items():
        full_path = f"{namespace}/{key}"
        secrets.set_secret(name=full_path, value=str(value), param_type=param_type)
        results.append(full_path)
        LOGGER.info(f"Created: {full_path}")

    return results


# =============================================================================
# Search/Query Operations
# =============================================================================


def search(
    pattern: str,
    contains: typing.Optional[str] = None,
    **kwargs,
) -> typing.List[str]:
    """
    Search parameters by name pattern (supports wildcards).
    Use fnmatch patterns like '/prod/*/api_key' or '*database*'.
    """
    secrets = _get_client(**kwargs)
    all_keys = secrets.keys()

    results = []
    for key in all_keys:
        if fnmatch.fnmatch(key, pattern):
            results.append(key)
        elif contains and contains in key:
            results.append(key)

    return sorted(set(results))


def grep(
    pattern: str,
    path_prefix: str = "/",
    regex: bool = False,
    **kwargs,
) -> typing.Dict[str, str]:
    """
    Search parameters by value content.
    Returns dict of matching {name: value} pairs.
    """
    secrets = _get_client(**kwargs)
    params = secrets.under(path_prefix)

    results = {}
    for name, value in params.items():
        if regex:
            if re.search(pattern, value):
                results[name] = value
        else:
            if pattern in value:
                results[name] = value

    return results


def count(
    path_prefix: str = "/",
    by_type: bool = False,
    **kwargs,
) -> typing.Union[int, typing.Dict[str, int]]:
    """
    Count parameters under a path.
    With --by-type, returns breakdown by parameter type.
    """
    env = _get_env(**kwargs)
    paginator = env.ssm.get_paginator("describe_parameters")
    pager = paginator.paginate(
        ParameterFilters=[
            dict(Key="Path", Option="Recursive", Values=[path_prefix])
        ]
    )

    if by_type:
        counts = {"SecureString": 0, "String": 0, "StringList": 0}
        for page in pager:
            for param in page["Parameters"]:
                param_type = param.get("Type", "Unknown")
                counts[param_type] = counts.get(param_type, 0) + 1
        return counts
    else:
        total = 0
        for page in pager:
            total += len(page["Parameters"])
        return total


def tree(
    path_prefix: str = "/",
    show_types: bool = False,
    show_modified: bool = False,
    max_depth: typing.Optional[int] = None,
    **kwargs,
) -> typing.Dict:
    """
    Build a tree structure of parameters with optional metadata.
    """
    env = _get_env(**kwargs)
    secrets = env.secrets
    params = secrets.under(path_prefix)

    # Get metadata if needed
    metadata = {}
    if show_types or show_modified:
        paginator = env.ssm.get_paginator("describe_parameters")
        pager = paginator.paginate(
            ParameterFilters=[
                dict(Key="Path", Option="Recursive", Values=[path_prefix])
            ]
        )
        for page in pager:
            for p in page["Parameters"]:
                metadata[p["Name"]] = {
                    "type": p.get("Type"),
                    "modified": str(p.get("LastModifiedDate", "")),
                }

    # Build tree structure
    def build_tree(items, prefix, depth=0):
        if max_depth is not None and depth >= max_depth:
            return {"...": f"{len(items)} items"}

        tree_dict = {}
        grouped = {}

        for path, value in items.items():
            relative = path[len(prefix) :].lstrip("/")
            parts = relative.split("/")
            if len(parts) == 1:
                # Leaf node
                leaf_info = value
                if show_types or show_modified:
                    meta = metadata.get(path, {})
                    info_parts = []
                    if show_types and meta.get("type"):
                        info_parts.append(meta["type"])
                    if show_modified and meta.get("modified"):
                        info_parts.append(f"modified: {meta['modified'][:10]}")
                    if info_parts:
                        leaf_info = f"({', '.join(info_parts)})"
                tree_dict[parts[0]] = leaf_info
            else:
                # Group by first component
                first = parts[0]
                if first not in grouped:
                    grouped[first] = {}
                grouped[first][path] = value

        # Recursively build subtrees
        for group_name, group_items in grouped.items():
            new_prefix = f"{prefix.rstrip('/')}/{group_name}"
            tree_dict[group_name] = build_tree(group_items, new_prefix, depth + 1)

        return tree_dict

    return build_tree(params, path_prefix)


def diff(
    src_path: str,
    dst_path: str,
    src_profile: str = "default",
    dst_profile: str = "default",
    show_values: bool = False,
    **kwargs,
) -> typing.Dict[str, typing.Any]:
    """
    Compare parameters between two paths/environments.
    Returns dict with 'only_in_src', 'only_in_dst', 'different', 'identical_count'.
    """
    src_man = _get_client(profile=src_profile)
    dst_man = _get_client(profile=dst_profile)

    src_path = src_path.rstrip("/")
    dst_path = dst_path.rstrip("/")

    src_params = src_man.under(src_path)
    dst_params = dst_man.under(dst_path)

    def normalize_key(key, prefix):
        return key[len(prefix) :] if key.startswith(prefix) else key

    src_normalized = {normalize_key(k, src_path): v for k, v in src_params.items()}
    dst_normalized = {normalize_key(k, dst_path): v for k, v in dst_params.items()}

    src_keys = set(src_normalized.keys())
    dst_keys = set(dst_normalized.keys())

    only_in_src = sorted(src_keys - dst_keys)
    only_in_dst = sorted(dst_keys - src_keys)
    common_keys = src_keys & dst_keys

    different = []
    identical = []

    for key in sorted(common_keys):
        src_val = src_normalized[key]
        dst_val = dst_normalized[key]
        if src_val != dst_val:
            if show_values:
                different.append({"key": key, "src": src_val, "dst": dst_val})
            else:
                different.append(key)
        else:
            identical.append(key)

    return {
        "only_in_src": [f"{src_path}{k}" for k in only_in_src],
        "only_in_dst": [f"{dst_path}{k}" for k in only_in_dst],
        "different": different,
        "identical_count": len(identical),
    }


# =============================================================================
# History/Versioning
# =============================================================================


def history(
    secret_name: str,
    max_results: int = 10,
    **kwargs,
) -> typing.List[typing.Dict]:
    """
    Get version history for a parameter.
    Returns list of version info dicts.
    """
    env = _get_env(**kwargs)
    paginator = env.ssm.get_paginator("get_parameter_history")
    pages = paginator.paginate(
        Name=secret_name,
        WithDecryption=True,
        PaginationConfig={"MaxItems": max_results},
    )

    results = []
    for page in pages:
        for param in page["Parameters"]:
            results.append(
                {
                    "version": param.get("Version"),
                    "value": param.get("Value"),
                    "type": param.get("Type"),
                    "last_modified": str(param.get("LastModifiedDate", "")),
                    "last_modified_user": param.get("LastModifiedUser", ""),
                }
            )

    return results


# =============================================================================
# Tags
# =============================================================================


def tags(secret_name: str, **kwargs) -> typing.List[typing.Dict[str, str]]:
    """
    Get tags for a parameter.
    """
    env = _get_env(**kwargs)
    response = env.ssm.list_tags_for_resource(
        ResourceType="Parameter",
        ResourceId=secret_name,
    )
    return response.get("TagList", [])


def add_tags(
    secret_name: str,
    tag_list: typing.List[typing.Tuple[str, str]],
    **kwargs,
) -> bool:
    """
    Add tags to a parameter.
    tag_list is a list of (key, value) tuples.
    """
    env = _get_env(**kwargs)
    env.ssm.add_tags_to_resource(
        ResourceType="Parameter",
        ResourceId=secret_name,
        Tags=[{"Key": k, "Value": v} for k, v in tag_list],
    )
    LOGGER.info(f"Added {len(tag_list)} tags to {secret_name}")
    return True


def remove_tags(
    secret_name: str,
    tag_keys: typing.List[str],
    **kwargs,
) -> bool:
    """
    Remove tags from a parameter by key names.
    """
    env = _get_env(**kwargs)
    env.ssm.remove_tags_from_resource(
        ResourceType="Parameter",
        ResourceId=secret_name,
        TagKeys=tag_keys,
    )
    LOGGER.info(f"Removed {len(tag_keys)} tags from {secret_name}")
    return True


# =============================================================================
# Sync Operations
# =============================================================================


def sync_pull(
    path_prefix: str,
    output_file: str,
    format: str = "yaml",
    **kwargs,
) -> str:
    """
    Pull parameters from SSM to a local file.
    """
    secrets = _get_client(**kwargs)
    params = secrets.under(path_prefix)

    # Convert to relative paths
    prefix_len = len(path_prefix.rstrip("/"))
    data = {}
    for k, v in params.items():
        relative_key = k[prefix_len:].lstrip("/")
        data[relative_key] = v

    with open(output_file, "w") as f:
        if format in ["yaml", "yml"]:
            yaml.dump(data, f, default_flow_style=False)
        elif format == "json":
            json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    LOGGER.info(f"Pulled {len(data)} parameters to {output_file}")
    return output_file


def sync_push(
    path_prefix: str,
    input_file: str,
    format: str = "yaml",
    dry_run: bool = False,
    delete_missing: bool = False,
    **kwargs,
) -> typing.Dict[str, typing.List[str]]:
    """
    Push parameters from a local file to SSM.
    With --delete-missing, removes parameters not in the file.
    """
    with open(input_file) as f:
        if format in ["yaml", "yml"]:
            data = yaml.safe_load(f) or {}
        elif format == "json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

    secrets = _get_client(**kwargs)
    existing = secrets.under(path_prefix)
    path_prefix = path_prefix.rstrip("/")

    # Build full paths for local data
    local_params = {f"{path_prefix}/{k}": v for k, v in data.items()}

    created = []
    updated = []
    deleted = []
    unchanged = []

    # Find what needs to be created/updated
    for path, value in local_params.items():
        if path not in existing:
            if dry_run:
                LOGGER.info(f"[DRY-RUN] Would create: {path}")
            else:
                secrets[path] = str(value)
                LOGGER.info(f"Created: {path}")
            created.append(path)
        elif existing[path] != str(value):
            if dry_run:
                LOGGER.info(f"[DRY-RUN] Would update: {path}")
            else:
                secrets[path] = str(value)
                LOGGER.info(f"Updated: {path}")
            updated.append(path)
        else:
            unchanged.append(path)

    # Find what needs to be deleted
    if delete_missing:
        for path in existing:
            if path not in local_params:
                if dry_run:
                    LOGGER.info(f"[DRY-RUN] Would delete: {path}")
                else:
                    del secrets[path]
                    LOGGER.info(f"Deleted: {path}")
                deleted.append(path)

    return {
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "unchanged": unchanged,
    }


def sync_diff(
    path_prefix: str,
    input_file: str,
    format: str = "yaml",
    **kwargs,
) -> typing.Dict[str, typing.Any]:
    """
    Show differences between local file and SSM parameters.
    """
    with open(input_file) as f:
        if format in ["yaml", "yml"]:
            data = yaml.safe_load(f) or {}
        elif format == "json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

    secrets = _get_client(**kwargs)
    existing = secrets.under(path_prefix)
    path_prefix = path_prefix.rstrip("/")

    local_params = {f"{path_prefix}/{k}": v for k, v in data.items()}

    only_local = []
    only_remote = []
    different = []
    identical = 0

    for path, value in local_params.items():
        if path not in existing:
            only_local.append(path)
        elif existing[path] != str(value):
            different.append(path)
        else:
            identical += 1

    for path in existing:
        if path not in local_params:
            only_remote.append(path)

    return {
        "only_in_local": only_local,
        "only_in_remote": only_remote,
        "different": different,
        "identical_count": identical,
    }


# =============================================================================
# Backup/Restore
# =============================================================================


def backup(
    path_prefix: str,
    output_file: str,
    include_metadata: bool = True,
    **kwargs,
) -> str:
    """
    Create a full backup of parameters to a compressed archive.
    Includes values and optionally metadata (types, descriptions, tags).
    """
    env = _get_env(**kwargs)
    secrets = env.secrets
    params = secrets.under(path_prefix)

    backup_data = {
        "version": "1.0",
        "created": datetime.datetime.utcnow().isoformat(),
        "path_prefix": path_prefix,
        "parameters": {},
    }

    # Get metadata
    if include_metadata:
        paginator = env.ssm.get_paginator("describe_parameters")
        pager = paginator.paginate(
            ParameterFilters=[
                dict(Key="Path", Option="Recursive", Values=[path_prefix])
            ]
        )
        metadata = {}
        for page in pager:
            for p in page["Parameters"]:
                metadata[p["Name"]] = {
                    "type": p.get("Type"),
                    "description": p.get("Description"),
                    "key_id": p.get("KeyId"),
                    "tier": p.get("Tier"),
                }

    for name, value in params.items():
        param_data = {"value": value}
        if include_metadata and name in metadata:
            param_data.update(metadata[name])
            # Get tags
            try:
                param_tags = tags(name, **kwargs)
                if param_tags:
                    param_data["tags"] = param_tags
            except Exception:
                pass
        backup_data["parameters"][name] = param_data

    # Write to compressed archive
    with gzip.open(output_file, "wt") as f:
        json.dump(backup_data, f, indent=2, default=str)

    LOGGER.info(f"Backed up {len(params)} parameters to {output_file}")
    return output_file


def restore(
    input_file: str,
    target_prefix: typing.Optional[str] = None,
    dry_run: bool = False,
    overwrite: bool = False,
    **kwargs,
) -> typing.Dict[str, typing.List[str]]:
    """
    Restore parameters from a backup archive.
    Optionally restore to a different path prefix.
    """
    with gzip.open(input_file, "rt") as f:
        backup_data = json.load(f)

    original_prefix = backup_data.get("path_prefix", "/")
    parameters = backup_data.get("parameters", {})

    secrets = _get_client(**kwargs)
    existing = set(secrets.keys())

    created = []
    updated = []
    skipped = []

    for name, param_data in parameters.items():
        # Optionally remap to new prefix
        if target_prefix:
            relative = name[len(original_prefix.rstrip("/")) :]
            new_name = f"{target_prefix.rstrip('/')}{relative}"
        else:
            new_name = name

        value = param_data.get("value", "")
        param_type = param_data.get("type", "SecureString")

        if new_name in existing and not overwrite:
            if dry_run:
                LOGGER.info(f"[DRY-RUN] Would skip (exists): {new_name}")
            skipped.append(new_name)
            continue

        if dry_run:
            action = "update" if new_name in existing else "create"
            LOGGER.info(f"[DRY-RUN] Would {action}: {new_name}")
        else:
            secrets.set_secret(
                name=new_name,
                value=value,
                param_type=param_type,
                description=param_data.get("description"),
            )
            # Restore tags
            if param_data.get("tags"):
                tag_list = [(t["Key"], t["Value"]) for t in param_data["tags"]]
                add_tags(new_name, tag_list, **kwargs)

        if new_name in existing:
            updated.append(new_name)
        else:
            created.append(new_name)

    LOGGER.info(
        f"Restore complete: {len(created)} created, {len(updated)} updated, {len(skipped)} skipped"
    )
    return {"created": created, "updated": updated, "skipped": skipped}


# =============================================================================
# Environment Export
# =============================================================================


def env_export(
    path_prefix: str,
    prefix: str = "",
    docker: bool = False,
    quote: bool = True,
    **kwargs,
) -> str:
    """
    Export parameters as environment variables (.env format).
    """
    secrets = _get_client(**kwargs)
    params = secrets.under(path_prefix)

    lines = []
    for name, value in sorted(params.items()):
        # Extract just the key name (last path component)
        key = name.split("/")[-1]
        # Convert to uppercase and replace dashes with underscores
        key = key.upper().replace("-", "_")
        # Add prefix if specified
        if prefix:
            key = f"{prefix}{key}"

        # Handle values with special characters
        if quote and ('"' in value or "'" in value or " " in value or "\n" in value):
            # Escape existing quotes and wrap in quotes
            value = value.replace("\\", "\\\\").replace('"', '\\"')
            value = f'"{value}"'
        elif quote and any(c in value for c in ["$", "`", "!", "#"]):
            value = f"'{value}'"

        if docker:
            lines.append(f"--env {key}={value}")
        else:
            lines.append(f"{key}={value}")

    return "\n".join(lines)


# =============================================================================
# Parameter Policies
# =============================================================================


def get_policy(secret_name: str, **kwargs) -> typing.Optional[typing.Dict]:
    """
    Get the policy for a parameter (expiration, notification).
    """
    env = _get_env(**kwargs)
    try:
        response = env.ssm.get_parameter(Name=secret_name)
        param = response.get("Parameter", {})
        policies = param.get("Policies", [])
        if policies:
            return {"name": secret_name, "policies": policies}
        return {"name": secret_name, "policies": []}
    except botocore.exceptions.ClientError as e:
        LOGGER.error(f"Error getting policy: {e}")
        return None


def set_policy(
    secret_name: str,
    expiration_days: typing.Optional[int] = None,
    notify_before_days: typing.Optional[int] = None,
    no_change_days: typing.Optional[int] = None,
    **kwargs,
) -> bool:
    """
    Set policies on a parameter (expiration, notification).
    Requires Advanced tier parameter.
    """
    env = _get_env(**kwargs)

    policies = []
    if expiration_days:
        policies.append(
            {
                "Type": "Expiration",
                "Version": "1.0",
                "Attributes": {"Timestamp": f"+{expiration_days}d"},
            }
        )
    if notify_before_days:
        policies.append(
            {
                "Type": "ExpirationNotification",
                "Version": "1.0",
                "Attributes": {"Before": str(notify_before_days), "Unit": "Days"},
            }
        )
    if no_change_days:
        policies.append(
            {
                "Type": "NoChangeNotification",
                "Version": "1.0",
                "Attributes": {"After": str(no_change_days), "Unit": "Days"},
            }
        )

    if not policies:
        LOGGER.warning("No policies specified")
        return False

    # Get current parameter
    try:
        current = env.ssm.get_parameter(Name=secret_name, WithDecryption=True)
        value = current["Parameter"]["Value"]
        param_type = current["Parameter"]["Type"]
    except botocore.exceptions.ClientError as e:
        LOGGER.error(f"Error getting parameter: {e}")
        return False

    # Update with policies
    try:
        env.ssm.put_parameter(
            Name=secret_name,
            Value=value,
            Type=param_type,
            Overwrite=True,
            Tier="Advanced",
            Policies=json.dumps(policies),
        )
        LOGGER.info(f"Set {len(policies)} policies on {secret_name}")
        return True
    except botocore.exceptions.ClientError as e:
        LOGGER.error(f"Error setting policy: {e}")
        return False


# =============================================================================
# Watch/Monitor
# =============================================================================


def watch(
    path_prefix: str,
    interval: int = 5,
    callback: typing.Optional[typing.Callable] = None,
    **kwargs,
) -> typing.Generator[typing.Dict, None, None]:
    """
    Watch for changes to parameters under a path.
    Yields change events as they occur.
    """
    secrets = _get_client(**kwargs)
    previous = secrets.under(path_prefix)
    previous_keys = set(previous.keys())

    LOGGER.info(f"Watching {path_prefix} (interval: {interval}s)")
    LOGGER.info(f"Initial state: {len(previous)} parameters")

    while True:
        time.sleep(interval)
        current = secrets.under(path_prefix)
        current_keys = set(current.keys())

        # Check for changes
        added = current_keys - previous_keys
        removed = previous_keys - current_keys
        common = current_keys & previous_keys

        modified = []
        for key in common:
            if current[key] != previous[key]:
                modified.append(key)

        if added or removed or modified:
            event = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "added": list(added),
                "removed": list(removed),
                "modified": modified,
            }

            if callback:
                callback(event)

            yield event

        previous = current
        previous_keys = current_keys


# =============================================================================
# Templates
# =============================================================================


def put_template(
    namespace: str,
    template_file: str,
    vars: typing.Dict[str, str],
    dry_run: bool = False,
    **kwargs,
) -> typing.List[str]:
    """
    Create parameters from a template file with variable substitution.
    Template uses {{VAR_NAME}} syntax.
    """
    with open(template_file) as f:
        content = f.read()

    # Substitute variables
    for key, value in vars.items():
        content = content.replace(f"{{{{{key}}}}}", value)

    # Check for unsubstituted variables
    unsubstituted = re.findall(r"\{\{(\w+)\}\}", content)
    if unsubstituted:
        LOGGER.warning(f"Unsubstituted variables: {unsubstituted}")

    # Parse the substituted content
    if template_file.endswith((".yaml", ".yml")):
        data = yaml.safe_load(content)
    elif template_file.endswith(".json"):
        data = json.loads(content)
    else:
        raise ValueError("Template must be .yaml, .yml, or .json")

    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in template, got {type(data)}")

    namespace = namespace.rstrip("/")

    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would create {len(data)} parameters from template:")
        for key, value in data.items():
            LOGGER.info(f"  - {namespace}/{key}: {value[:50]}...")
        return [f"{namespace}/{k}" for k in data.keys()]

    secrets = _get_client(**kwargs)
    results = []
    for key, value in data.items():
        full_path = f"{namespace}/{key}"
        secrets[full_path] = str(value)
        results.append(full_path)
        LOGGER.info(f"Created from template: {full_path}")

    return results


# =============================================================================
# Validation
# =============================================================================


def validate(
    path_prefix: str,
    schema_file: typing.Optional[str] = None,
    exists: bool = False,
    **kwargs,
) -> typing.Dict[str, typing.Any]:
    """
    Validate parameters against a schema or existence check.
    """
    secrets = _get_client(**kwargs)
    params = secrets.under(path_prefix)

    result = {
        "valid": True,
        "path": path_prefix,
        "count": len(params),
        "errors": [],
        "warnings": [],
    }

    if exists and not params:
        result["valid"] = False
        result["errors"].append(f"No parameters found under {path_prefix}")
        return result

    if schema_file:
        with open(schema_file) as f:
            schema = json.load(f)

        # Check required parameters
        for required in schema.get("required", []):
            full_path = f"{path_prefix.rstrip('/')}/{required}"
            if full_path not in params:
                result["valid"] = False
                result["errors"].append(f"Missing required parameter: {required}")

        # Check patterns
        for param_name, rules in schema.get("parameters", {}).items():
            full_path = f"{path_prefix.rstrip('/')}/{param_name}"
            if full_path in params:
                value = params[full_path]

                # Check pattern
                if "pattern" in rules:
                    if not re.match(rules["pattern"], value):
                        result["valid"] = False
                        result["errors"].append(
                            f"{param_name}: value doesn't match pattern {rules['pattern']}"
                        )

                # Check min/max length
                if "minLength" in rules and len(value) < rules["minLength"]:
                    result["valid"] = False
                    result["errors"].append(
                        f"{param_name}: value too short (min: {rules['minLength']})"
                    )
                if "maxLength" in rules and len(value) > rules["maxLength"]:
                    result["valid"] = False
                    result["errors"].append(
                        f"{param_name}: value too long (max: {rules['maxLength']})"
                    )

                # Check enum
                if "enum" in rules and value not in rules["enum"]:
                    result["valid"] = False
                    result["errors"].append(
                        f"{param_name}: value not in allowed values {rules['enum']}"
                    )

    return result


def lint(
    input_file: str,
    format: str = "yaml",
    **kwargs,
) -> typing.Dict[str, typing.Any]:
    """
    Lint a parameters file before pushing.
    Checks for common issues.
    """
    result = {
        "valid": True,
        "file": input_file,
        "errors": [],
        "warnings": [],
    }

    try:
        with open(input_file) as f:
            if format in ["yaml", "yml"]:
                data = yaml.safe_load(f)
            elif format == "json":
                data = json.load(f)
            else:
                result["valid"] = False
                result["errors"].append(f"Unsupported format: {format}")
                return result
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Parse error: {e}")
        return result

    if not isinstance(data, dict):
        result["valid"] = False
        result["errors"].append(f"Expected dict, got {type(data)}")
        return result

    for key, value in data.items():
        # Check key format
        if not re.match(r"^[\w\-\.]+$", key):
            result["warnings"].append(
                f"Key '{key}' contains special characters"
            )

        # Check for empty values
        if value is None or (isinstance(value, str) and not value.strip()):
            result["warnings"].append(f"Key '{key}' has empty value")

        # Check for potential secrets in plain text
        if isinstance(value, str):
            if re.search(r"(password|secret|key|token)\s*[:=]\s*\S+", value, re.I):
                result["warnings"].append(
                    f"Key '{key}' may contain embedded credentials"
                )

    result["parameter_count"] = len(data)
    return result


# =============================================================================
# Audit
# =============================================================================


def audit(
    path_prefix: str = "/",
    since: str = "7d",
    who: typing.Optional[str] = None,
    action: typing.Optional[str] = None,
    **kwargs,
) -> typing.List[typing.Dict]:
    """
    Query CloudTrail for SSM parameter access events.
    Requires CloudTrail to be enabled.
    """
    env = _get_env(**kwargs)

    # Parse since duration
    match = re.match(r"(\d+)([hdwm])", since)
    if match:
        amount, unit = int(match.group(1)), match.group(2)
        units = {"h": "hours", "d": "days", "w": "weeks", "m": "months"}
        if unit == "m":
            delta = datetime.timedelta(days=amount * 30)
        elif unit == "w":
            delta = datetime.timedelta(weeks=amount)
        elif unit == "d":
            delta = datetime.timedelta(days=amount)
        else:
            delta = datetime.timedelta(hours=amount)
        start_time = datetime.datetime.utcnow() - delta
    else:
        start_time = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    try:
        cloudtrail = env.session.client("cloudtrail")
    except Exception as e:
        LOGGER.error(f"Could not create CloudTrail client: {e}")
        return []

    # Build lookup attributes
    lookup_attrs = [{"AttributeKey": "EventSource", "AttributeValue": "ssm.amazonaws.com"}]

    if who:
        lookup_attrs.append({"AttributeKey": "Username", "AttributeValue": who})

    try:
        paginator = cloudtrail.get_paginator("lookup_events")
        pages = paginator.paginate(
            LookupAttributes=lookup_attrs,
            StartTime=start_time,
            EndTime=datetime.datetime.utcnow(),
        )

        events = []
        for page in pages:
            for event in page.get("Events", []):
                event_name = event.get("EventName", "")

                # Filter by action if specified
                if action and action.lower() not in event_name.lower():
                    continue

                # Parse CloudTrail event
                try:
                    detail = json.loads(event.get("CloudTrailEvent", "{}"))
                except json.JSONDecodeError:
                    detail = {}

                # Check if event relates to our path prefix
                request_params = detail.get("requestParameters", {})
                param_name = request_params.get("name", request_params.get("names", [""])[0] if isinstance(request_params.get("names"), list) else "")

                if path_prefix != "/" and not param_name.startswith(path_prefix):
                    continue

                events.append({
                    "timestamp": str(event.get("EventTime", "")),
                    "event": event_name,
                    "user": event.get("Username", ""),
                    "parameter": param_name,
                    "source_ip": detail.get("sourceIPAddress", ""),
                    "user_agent": detail.get("userAgent", "")[:50] if detail.get("userAgent") else "",
                })

        return events[:100]  # Limit results

    except botocore.exceptions.ClientError as e:
        LOGGER.error(f"CloudTrail lookup failed: {e}")
        return []


# =============================================================================
# Secret Rotation
# =============================================================================


def generate_secret(
    length: int = 32,
    chars: str = "alphanumeric",
    exclude: str = "",
) -> str:
    """
    Generate a random secret value.
    chars options: alphanumeric, alpha, numeric, special, all
    """
    char_sets = {
        "alpha": string.ascii_letters,
        "numeric": string.digits,
        "alphanumeric": string.ascii_letters + string.digits,
        "special": string.punctuation,
        "all": string.ascii_letters + string.digits + string.punctuation,
    }

    charset = char_sets.get(chars, chars)  # Allow custom charset
    if exclude:
        charset = "".join(c for c in charset if c not in exclude)

    return "".join(secrets_module.choice(charset) for _ in range(length))


def rotate(
    secret_name: str,
    length: int = 32,
    chars: str = "alphanumeric",
    dry_run: bool = False,
    **kwargs,
) -> typing.Dict[str, str]:
    """
    Rotate a secret by generating a new random value.
    Returns old and new values.
    """
    secrets = _get_client(**kwargs)

    # Get old value
    try:
        old_value = secrets[secret_name]
    except KeyError:
        old_value = None
        LOGGER.warning(f"Parameter {secret_name} doesn't exist, will create")

    # Generate new value
    new_value = generate_secret(length=length, chars=chars)

    if dry_run:
        LOGGER.info(f"[DRY-RUN] Would rotate {secret_name}")
        LOGGER.info(f"  New value length: {len(new_value)}")
        return {"name": secret_name, "rotated": False, "dry_run": True}

    # Update the secret
    secrets[secret_name] = new_value
    LOGGER.info(f"Rotated: {secret_name}")

    return {
        "name": secret_name,
        "old_value": old_value,
        "new_value": new_value,
        "rotated": True,
    }


# =============================================================================
# KMS Operations
# =============================================================================


def rekey(
    path_prefix: str,
    from_key: str,
    to_key: str,
    dry_run: bool = False,
    **kwargs,
) -> typing.List[str]:
    """
    Re-encrypt parameters with a new KMS key.
    """
    env = _get_env(**kwargs)
    secrets = env.secrets
    params = secrets.under(path_prefix)

    rekeyed = []
    for name, value in params.items():
        if dry_run:
            LOGGER.info(f"[DRY-RUN] Would rekey: {name}")
        else:
            # Re-put with new KMS key
            env.ssm.put_parameter(
                Name=name,
                Value=value,
                Type="SecureString",
                KeyId=to_key,
                Overwrite=True,
            )
            LOGGER.info(f"Rekeyed: {name}")
        rekeyed.append(name)

    return rekeyed


def list_by_kms(
    kms_key: str,
    path_prefix: str = "/",
    **kwargs,
) -> typing.List[str]:
    """
    List parameters encrypted with a specific KMS key.
    """
    env = _get_env(**kwargs)
    paginator = env.ssm.get_paginator("describe_parameters")
    pager = paginator.paginate(
        ParameterFilters=[
            dict(Key="Path", Option="Recursive", Values=[path_prefix])
        ]
    )

    results = []
    for page in pager:
        for param in page["Parameters"]:
            if param.get("KeyId") == kms_key or kms_key in param.get("KeyId", ""):
                results.append(param["Name"])

    return results


# =============================================================================
# CI/CD Helpers
# =============================================================================


def inject(
    template_file: str,
    output_file: typing.Optional[str] = None,
    path_prefix: str = "/",
    **kwargs,
) -> str:
    """
    Inject SSM parameter values into a template file.
    Replaces {{SSM:/path/to/param}} with actual values.
    """
    secrets = _get_client(**kwargs)

    with open(template_file) as f:
        content = f.read()

    # Find all SSM references
    pattern = r"\{\{SSM:([^}]+)\}\}"
    matches = re.findall(pattern, content)

    for param_path in matches:
        try:
            value = secrets[param_path]
            content = content.replace(f"{{{{SSM:{param_path}}}}}", value)
            LOGGER.debug(f"Injected: {param_path}")
        except KeyError:
            LOGGER.warning(f"Parameter not found: {param_path}")

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        return output_file
    else:
        return content


def verify_access(
    path_prefix: str,
    **kwargs,
) -> typing.Dict[str, typing.Any]:
    """
    Verify access to parameters under a path.
    Returns access status and any errors.
    Useful for CI/CD pipeline checks.
    """
    result = {
        "accessible": True,
        "path": path_prefix,
        "readable_count": 0,
        "errors": [],
    }

    try:
        secrets = _get_client(**kwargs)
        params = secrets.under(path_prefix)
        result["readable_count"] = len(params)

        if not params:
            result["warnings"] = [f"No parameters found under {path_prefix}"]

    except botocore.exceptions.ClientError as e:
        result["accessible"] = False
        result["errors"].append(str(e))
    except Exception as e:
        result["accessible"] = False
        result["errors"].append(str(e))

    return result


# =============================================================================
# Terraform Integration
# =============================================================================


def export_terraform(
    path_prefix: str,
    **kwargs,
) -> str:
    """
    Export parameters as Terraform aws_ssm_parameter resources.
    """
    env = _get_env(**kwargs)
    secrets = env.secrets
    params = secrets.under(path_prefix)

    # Get metadata
    paginator = env.ssm.get_paginator("describe_parameters")
    pager = paginator.paginate(
        ParameterFilters=[
            dict(Key="Path", Option="Recursive", Values=[path_prefix])
        ]
    )
    metadata = {}
    for page in pager:
        for p in page["Parameters"]:
            metadata[p["Name"]] = {
                "type": p.get("Type"),
                "description": p.get("Description"),
                "tier": p.get("Tier"),
            }

    tf_resources = []
    for name, value in params.items():
        # Create valid Terraform resource name
        resource_name = name.replace("/", "_").replace("-", "_").strip("_")
        meta = metadata.get(name, {})

        resource = f'''resource "aws_ssm_parameter" "{resource_name}" {{
  name        = "{name}"
  description = "{meta.get('description', '')}"
  type        = "{meta.get('type', 'SecureString')}"
  value       = "{value}"
  tier        = "{meta.get('tier', 'Standard')}"

  tags = {{
    ManagedBy = "terraform"
  }}
}}
'''
        tf_resources.append(resource)

    return "\n".join(tf_resources)


# =============================================================================
# Kubernetes Integration
# =============================================================================


def k8s_export(
    path_prefix: str,
    secret_name: str = "app-secrets",
    namespace: str = "default",
    **kwargs,
) -> str:
    """
    Export parameters as a Kubernetes Secret manifest.
    """
    secrets = _get_client(**kwargs)
    params = secrets.under(path_prefix)

    # Build data section with base64 encoded values
    data = {}
    for name, value in params.items():
        # Use last path component as key
        key = name.split("/")[-1]
        # Kubernetes secret keys have restrictions
        key = re.sub(r"[^a-zA-Z0-9\-_.]", "_", key)
        data[key] = base64.b64encode(value.encode()).decode()

    manifest = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": secret_name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/managed-by": "ssm-tool",
            },
            "annotations": {
                "ssm-tool/source-path": path_prefix,
            },
        },
        "type": "Opaque",
        "data": data,
    }

    return yaml.dump(manifest, default_flow_style=False)
