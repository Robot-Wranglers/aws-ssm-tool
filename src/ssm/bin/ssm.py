""" ssm.bin.ssm

  Command-line entry-points.
  (This file makes parts of `ssm.api` available via click)
"""

import functools
import json
import sys

import click
import yaml

from ssm import api, cli, util
from ssm.cli import completion
from ssm.cli.wrapper import ApiWrapper

LOGGER = util.get_logger(__name__)


@click.command(cls=cli.Group)
def entry(*args, **kargs):  # noqa
    """
    SSM tool, a small helper for interacting with Amazon Simple Systems Manager
    for secrets storage/retrieval.

    Environment Variables:
        SSM_LOG_LEVEL: Set log verbosity (DEBUG, INFO, WARNING, ERROR)
        AWS_PROFILE: Default AWS profile to use
    """


ApiWrapper = functools.partial(
    ApiWrapper,
    entry=entry,
)

# =============================================================================
# Common options
# =============================================================================

dry_run_option = click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview changes without executing them.",
)

force_option = click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Skip confirmation prompts.",
)

param_type_option = click.option(
    "--type",
    "param_type",
    type=click.Choice(["SecureString", "String", "StringList"]),
    default="SecureString",
    show_default=True,
    help="Parameter type.",
)

stdin_option = click.option(
    "--stdin",
    is_flag=True,
    default=False,
    help="Read value from stdin.",
)

version_option = click.option(
    "--version",
    type=int,
    default=None,
    help="Parameter version number.",
)

# =============================================================================
# LIST COMMANDS
# =============================================================================

list = ApiWrapper(
    fxn=api.list,
    aliases=["ls"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_tree_default,
        cli.options.dirs_only,
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

list_dirs = ApiWrapper(
    fxn=api.list_dirs,
    aliases=["ls-dirs"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# READ COMMANDS
# =============================================================================

stat = ApiWrapper(
    fxn=api.stat,
    aliases=["st"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        cli.options.caller_context,
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

read = ApiWrapper(
    fxn=api.read,
    aliases=["get"],
    extra_options=[
        cli.options.profile,
        version_option,
        cli.args.secret_name,
    ],
)

get_many = ApiWrapper(
    fxn=api.get_many,
    aliases=["get-path"],
    extra_options=[
        cli.options.profile,
        cli.options.flat_output,
        cli.options.output_format_yaml_default,
        cli.args.namespace,
    ],
)

# =============================================================================
# WRITE COMMANDS
# =============================================================================

update = ApiWrapper(
    fxn=api.update,
    aliases=["put", "set"],
    extra_options=[
        cli.options.profile,
        cli.options.existing_file,
        stdin_option,
        param_type_option,
        click.argument("value", default="", nargs=1),
        cli.args.secret_name,
    ],
)

put_many = ApiWrapper(
    fxn=api.put_many,
    aliases=["put-path"],
    extra_options=[
        cli.options.profile,
        cli.options.existing_file,
        cli.options.output_format_yaml_default,
        dry_run_option,
        param_type_option,
        cli.args.namespace,
    ],
)

# =============================================================================
# DELETE COMMANDS
# =============================================================================

delete = ApiWrapper(
    fxn=api.delete,
    aliases=["rm"],
    extra_options=[
        cli.options.profile,
        cli.args.secret_name,
        dry_run_option,
        click.option(
            "--no-backup",
            is_flag=True,
            default=False,
            help="Do not create backup file.",
        ),
    ],
)

delete_path = ApiWrapper(
    fxn=api.delete_path,
    aliases=["rm-path"],
    extra_options=[
        cli.options.profile,
        dry_run_option,
        force_option,
        click.option(
            "--no-backup",
            is_flag=True,
            default=False,
            help="Do not create backup files.",
        ),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# COPY/MOVE COMMANDS
# =============================================================================

copy = ApiWrapper(
    fxn=api.copy,
    aliases=["cp"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        dry_run_option,
        click.argument("dst_name", nargs=1, shell_complete=completion.complete_parameters),
        click.argument("src_name", nargs=1, shell_complete=completion.complete_parameters),
    ],
)

copy_many = ApiWrapper(
    fxn=api.copy_many,
    aliases=["cp-many", "cp-path", "copy-path"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        dry_run_option,
        click.argument("dst_name", nargs=1, shell_complete=completion.complete_paths),
        click.argument("src_name", nargs=1, shell_complete=completion.complete_paths),
    ],
)

move = ApiWrapper(
    fxn=api.move,
    aliases=["mv"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        dry_run_option,
        click.argument("dst_name", nargs=1, shell_complete=completion.complete_parameters),
        click.argument("src_name", nargs=1, shell_complete=completion.complete_parameters),
    ],
)

move_many = ApiWrapper(
    fxn=api.move_many,
    aliases=["mv-many", "move-path", "mv-path"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        dry_run_option,
        click.argument("dst_name", nargs=1, shell_complete=completion.complete_paths),
        click.argument("src_name", nargs=1, shell_complete=completion.complete_paths),
    ],
)

rename = ApiWrapper(
    fxn=api.rename,
    aliases=["ren"],
    extra_options=[
        cli.options.profile,
        dry_run_option,
        click.argument("new_name", nargs=1),
        click.argument("old_name", nargs=1, shell_complete=completion.complete_parameters),
    ],
)

# =============================================================================
# SEARCH/QUERY COMMANDS
# =============================================================================

search = ApiWrapper(
    fxn=api.search,
    aliases=["find"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        click.option(
            "--contains",
            default=None,
            help="Also match parameters containing this string.",
        ),
        click.argument("pattern", nargs=1),
    ],
)

grep = ApiWrapper(
    fxn=api.grep,
    aliases=["grep-values"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.option(
            "--regex",
            "-r",
            is_flag=True,
            default=False,
            help="Treat pattern as regex.",
        ),
        click.option(
            "--path",
            "path_prefix",
            default="/",
            help="Path prefix to search under.",
        ),
        click.argument("pattern", nargs=1),
    ],
)

count = ApiWrapper(
    fxn=api.count,
    aliases=["cnt"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        click.option(
            "--by-type",
            is_flag=True,
            default=False,
            help="Break down count by parameter type.",
        ),
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

tree = ApiWrapper(
    fxn=api.tree,
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.option(
            "--show-types",
            is_flag=True,
            default=False,
            help="Show parameter types.",
        ),
        click.option(
            "--show-modified",
            is_flag=True,
            default=False,
            help="Show last modified dates.",
        ),
        click.option(
            "--max-depth",
            type=int,
            default=None,
            help="Maximum depth to display.",
        ),
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

diff = ApiWrapper(
    fxn=api.diff,
    aliases=["compare"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        cli.options.output_format_yaml_default,
        click.option(
            "--show-values",
            is_flag=True,
            default=False,
            help="Show actual values in diff output.",
        ),
        click.argument("dst_path", nargs=1, shell_complete=completion.complete_paths),
        click.argument("src_path", nargs=1, shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# HISTORY COMMANDS
# =============================================================================

history = ApiWrapper(
    fxn=api.history,
    aliases=["hist"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.option(
            "--max-results",
            type=int,
            default=10,
            help="Maximum number of versions to return.",
        ),
        cli.args.secret_name,
    ],
)

# =============================================================================
# TAG COMMANDS
# =============================================================================

tags = ApiWrapper(
    fxn=api.tags,
    aliases=["show-tags"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        cli.args.secret_name,
    ],
)


@entry.command(name="add-tags")
@cli.options.profile
@click.option("--tag", "-t", multiple=True, help="Tag in key=value format.")
@click.argument("secret_name", nargs=1, shell_complete=completion.complete_parameters)
def add_tags_cmd(profile, tag, secret_name):
    """Add tags to a parameter. Use --tag key=value (can be repeated)."""
    tag_list = []
    for t in tag:
        if "=" not in t:
            raise click.BadParameter(f"Tag must be in key=value format: {t}")
        k, v = t.split("=", 1)
        tag_list.append((k, v))

    if not tag_list:
        raise click.UsageError("At least one --tag is required")

    api.add_tags(secret_name, tag_list, profile=profile)
    click.echo(f"Added {len(tag_list)} tags to {secret_name}")


@entry.command(name="remove-tags")
@cli.options.profile
@click.option("--key", "-k", multiple=True, help="Tag key to remove.")
@click.argument("secret_name", nargs=1, shell_complete=completion.complete_parameters)
def remove_tags_cmd(profile, key, secret_name):
    """Remove tags from a parameter by key names."""
    if not key:
        raise click.UsageError("At least one --key is required")

    api.remove_tags(secret_name, list(key), profile=profile)
    click.echo(f"Removed {len(key)} tags from {secret_name}")


# =============================================================================
# SYNC COMMANDS
# =============================================================================

sync_pull = ApiWrapper(
    fxn=api.sync_pull,
    aliases=["pull"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.argument("output_file", nargs=1),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

sync_push = ApiWrapper(
    fxn=api.sync_push,
    aliases=["push"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        dry_run_option,
        click.option(
            "--delete-missing",
            is_flag=True,
            default=False,
            help="Delete parameters not in the input file.",
        ),
        click.argument("input_file", nargs=1),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

sync_diff = ApiWrapper(
    fxn=api.sync_diff,
    aliases=["sync-status"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.argument("input_file", nargs=1),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# BACKUP/RESTORE COMMANDS
# =============================================================================

backup = ApiWrapper(
    fxn=api.backup,
    extra_options=[
        cli.options.profile,
        click.option(
            "--no-metadata",
            "include_metadata",
            is_flag=True,
            flag_value=False,
            default=True,
            help="Exclude metadata (types, descriptions, tags).",
        ),
        click.argument("output_file", nargs=1),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

restore = ApiWrapper(
    fxn=api.restore,
    extra_options=[
        cli.options.profile,
        dry_run_option,
        click.option(
            "--target-prefix",
            default=None,
            help="Restore to a different path prefix.",
        ),
        click.option(
            "--overwrite",
            is_flag=True,
            default=False,
            help="Overwrite existing parameters.",
        ),
        click.argument("input_file", nargs=1),
    ],
)

# =============================================================================
# ENVIRONMENT EXPORT COMMANDS
# =============================================================================

env_export = ApiWrapper(
    fxn=api.env_export,
    aliases=["env", "dotenv"],
    extra_options=[
        cli.options.profile,
        click.option(
            "--prefix",
            default="",
            help="Prefix for environment variable names.",
        ),
        click.option(
            "--docker",
            is_flag=True,
            default=False,
            help="Format as docker --env flags.",
        ),
        click.option(
            "--no-quote",
            "quote",
            is_flag=True,
            flag_value=False,
            default=True,
            help="Don't quote values with special characters.",
        ),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# POLICY COMMANDS
# =============================================================================


@entry.command(name="get-policy")
@cli.options.profile
@click.argument("secret_name", nargs=1, shell_complete=completion.complete_parameters)
def get_policy_cmd(profile, secret_name):
    """Get the policy for a parameter (expiration, notification)."""
    result = api.get_policy(secret_name, profile=profile)
    if result:
        click.echo(yaml.dump(result, default_flow_style=False))
    else:
        click.echo("No policy found or error occurred.")


@entry.command(name="set-policy")
@cli.options.profile
@click.option(
    "--expiration-days",
    type=int,
    default=None,
    help="Days until parameter expires.",
)
@click.option(
    "--notify-before-days",
    type=int,
    default=None,
    help="Days before expiration to send notification.",
)
@click.option(
    "--no-change-days",
    type=int,
    default=None,
    help="Days without changes before notification.",
)
@click.argument("secret_name", nargs=1, shell_complete=completion.complete_parameters)
def set_policy_cmd(
    profile, expiration_days, notify_before_days, no_change_days, secret_name
):
    """Set policies on a parameter. Requires Advanced tier."""
    if not any([expiration_days, notify_before_days, no_change_days]):
        raise click.UsageError("At least one policy option is required")

    result = api.set_policy(
        secret_name,
        expiration_days=expiration_days,
        notify_before_days=notify_before_days,
        no_change_days=no_change_days,
        profile=profile,
    )
    if result:
        click.echo(f"Policy set for {secret_name}")
    else:
        click.echo("Failed to set policy")


# =============================================================================
# WATCH COMMAND
# =============================================================================


@entry.command(name="watch")
@cli.options.profile
@click.option(
    "--interval",
    type=int,
    default=5,
    show_default=True,
    help="Polling interval in seconds.",
)
@click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths)
def watch_cmd(profile, interval, path_prefix):
    """Watch for changes to parameters under a path."""
    click.echo(f"Watching {path_prefix} (interval: {interval}s, Ctrl+C to stop)...")
    try:
        for event in api.watch(path_prefix, interval=interval, profile=profile):
            click.echo(f"\n[{event['timestamp']}]")
            if event["added"]:
                click.echo(f"  Added: {', '.join(event['added'])}")
            if event["removed"]:
                click.echo(f"  Removed: {', '.join(event['removed'])}")
            if event["modified"]:
                click.echo(f"  Modified: {', '.join(event['modified'])}")
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")


# =============================================================================
# TEMPLATE COMMAND
# =============================================================================


@entry.command(name="put-template")
@cli.options.profile
@dry_run_option
@click.option(
    "--var",
    "-v",
    multiple=True,
    help="Variable in key=value format for template substitution.",
)
@click.argument("template_file", nargs=1)
@click.argument("namespace", nargs=1, shell_complete=completion.complete_paths)
def put_template_cmd(profile, dry_run, var, template_file, namespace):
    """Create parameters from a template file with variable substitution.

    Template uses {{VAR_NAME}} syntax for placeholders.
    """
    vars_dict = {}
    for v in var:
        if "=" not in v:
            raise click.BadParameter(f"Variable must be in key=value format: {v}")
        k, val = v.split("=", 1)
        vars_dict[k] = val

    result = api.put_template(
        namespace,
        template_file,
        vars=vars_dict,
        dry_run=dry_run,
        profile=profile,
    )
    click.echo(f"Created {len(result)} parameters from template")


# =============================================================================
# VALIDATION COMMANDS
# =============================================================================

validate = ApiWrapper(
    fxn=api.validate,
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.option(
            "--schema",
            "schema_file",
            type=click.Path(exists=True),
            default=None,
            help="JSON schema file for validation.",
        ),
        click.option(
            "--exists",
            is_flag=True,
            default=False,
            help="Only check that parameters exist.",
        ),
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

lint = ApiWrapper(
    fxn=api.lint,
    extra_options=[
        cli.options.output_format_yaml_default,
        click.argument("input_file", nargs=1),
    ],
)

# =============================================================================
# AUDIT COMMAND
# =============================================================================

audit = ApiWrapper(
    fxn=api.audit,
    aliases=["audit-log"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.option(
            "--since",
            default="7d",
            show_default=True,
            help="Time period (e.g., 1h, 7d, 2w, 1m).",
        ),
        click.option(
            "--who",
            default=None,
            help="Filter by username.",
        ),
        click.option(
            "--action",
            default=None,
            help="Filter by action (GetParameter, PutParameter, etc.).",
        ),
        click.argument("path_prefix", nargs=1, default="/", shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# ROTATION COMMANDS
# =============================================================================


@entry.command(name="generate-secret")
@click.option(
    "--length",
    type=int,
    default=32,
    show_default=True,
    help="Length of generated secret.",
)
@click.option(
    "--chars",
    type=click.Choice(["alphanumeric", "alpha", "numeric", "special", "all"]),
    default="alphanumeric",
    show_default=True,
    help="Character set to use.",
)
@click.option(
    "--exclude",
    default="",
    help="Characters to exclude from the secret.",
)
def generate_secret_cmd(length, chars, exclude):
    """Generate a random secret value."""
    secret = api.generate_secret(length=length, chars=chars, exclude=exclude)
    click.echo(secret)


@entry.command(name="rotate")
@cli.options.profile
@dry_run_option
@click.option(
    "--length",
    type=int,
    default=32,
    show_default=True,
    help="Length of new secret.",
)
@click.option(
    "--chars",
    type=click.Choice(["alphanumeric", "alpha", "numeric", "special", "all"]),
    default="alphanumeric",
    show_default=True,
    help="Character set to use.",
)
@click.argument("secret_name", nargs=1, shell_complete=completion.complete_parameters)
def rotate_cmd(profile, dry_run, length, chars, secret_name):
    """Rotate a secret by generating a new random value."""
    result = api.rotate(
        secret_name, length=length, chars=chars, dry_run=dry_run, profile=profile
    )
    if dry_run:
        click.echo(f"[DRY-RUN] Would rotate: {secret_name}")
    elif result.get("rotated"):
        click.echo(f"Rotated: {secret_name}")
        click.echo(f"New value: {result['new_value']}")
    else:
        click.echo("Rotation failed")


# =============================================================================
# KMS COMMANDS
# =============================================================================


@entry.command(name="rekey")
@cli.options.profile
@dry_run_option
@click.option("--from-key", required=True, help="Current KMS key ID or alias.")
@click.option("--to-key", required=True, help="New KMS key ID or alias.")
@click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths)
def rekey_cmd(profile, dry_run, from_key, to_key, path_prefix):
    """Re-encrypt parameters with a new KMS key."""
    result = api.rekey(
        path_prefix, from_key=from_key, to_key=to_key, dry_run=dry_run, profile=profile
    )
    click.echo(f"Re-keyed {len(result)} parameters")


list_by_kms = ApiWrapper(
    fxn=api.list_by_kms,
    aliases=["ls-kms"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        click.option(
            "--path",
            "path_prefix",
            default="/",
            help="Path prefix to search under.",
        ),
        click.argument("kms_key", nargs=1),
    ],
)

# =============================================================================
# CI/CD COMMANDS
# =============================================================================


@entry.command(name="inject")
@cli.options.profile
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Output file (default: stdout).",
)
@click.argument("template_file", nargs=1)
def inject_cmd(profile, output_file, template_file):
    """Inject SSM parameter values into a template file.

    Replaces {{SSM:/path/to/param}} with actual values.
    """
    result = api.inject(template_file, output_file=output_file, profile=profile)
    if not output_file:
        click.echo(result)
    else:
        click.echo(f"Injected to: {result}")


verify_access = ApiWrapper(
    fxn=api.verify_access,
    aliases=["check-access"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths),
    ],
)

# =============================================================================
# TERRAFORM COMMAND
# =============================================================================


@entry.command(name="export-terraform")
@cli.options.profile
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Output file (default: stdout).",
)
@click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths)
def export_terraform_cmd(profile, output_file, path_prefix):
    """Export parameters as Terraform aws_ssm_parameter resources."""
    result = api.export_terraform(path_prefix, profile=profile)
    if output_file:
        with open(output_file, "w") as f:
            f.write(result)
        click.echo(f"Exported to: {output_file}")
    else:
        click.echo(result)


# =============================================================================
# KUBERNETES COMMAND
# =============================================================================


@entry.command(name="k8s-export")
@cli.options.profile
@click.option(
    "--secret-name",
    default="app-secrets",
    show_default=True,
    help="Name for the Kubernetes Secret.",
)
@click.option(
    "--namespace",
    default="default",
    show_default=True,
    help="Kubernetes namespace.",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Output file (default: stdout).",
)
@click.argument("path_prefix", nargs=1, shell_complete=completion.complete_paths)
def k8s_export_cmd(profile, secret_name, namespace, output_file, path_prefix):
    """Export parameters as a Kubernetes Secret manifest."""
    result = api.k8s_export(
        path_prefix, secret_name=secret_name, namespace=namespace, profile=profile
    )
    if output_file:
        with open(output_file, "w") as f:
            f.write(result)
        click.echo(f"Exported to: {output_file}")
    else:
        click.echo(result)
