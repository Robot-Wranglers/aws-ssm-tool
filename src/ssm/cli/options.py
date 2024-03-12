""" ssm.cli.options (boilerplate for click)

    Common CLI arguments for reuse
"""

from functools import partial

import click

key = click.option("--key", help="key to use", default="", required=False)

top = click.option(
    "--top", help="triage and only describe top N results", required=False
)
existing_file = click.option("--file", type=click.Path(exists=True))
filter_service_partial = partial(
    click.option, "--service", help="filter for service", required=False
)
filter_service = filter_service_partial(default=".*")

output_format_partial = partial(
    click.option,
    "--format",
    show_default=True,
    type=click.Choice(["json", "yaml", "yml", "env", "stdout", "tree"]),
    help="output format",
)
output_format = format = output_format_partial(required=True)
output_format_yaml_default = output_format_partial(required=False, default="yaml")
output_format_json_default = output_format_partial(required=False, default="json")
output_format_stdout_default = output_format_partial(required=False, default="stdout")
output_format_tree_default = output_format_partial(required=False, default="tree")


optional_user = user = click.option(
    "--user",
    help="username (default will attempt auto-detect)",
    required=False,
    default="",
)
optional_users = users = click.option(
    "--users", help="user list (comma-separatted)", required=False, default=""
)

raw = click.option(
    "--raw", "-r", help="unquotes text return values (like jq -r)", default=False
)

force_or_dry = force = dry_run = click.option(
    "--force/--dry-run", "-f/-d", help="perform actions", default=False, envvar="FORCE"
)

pause_or_nowait = no_wait = pause = click.option(
    "--pause/--no-wait", help="pause before starting", default=True
)

optional_prefix = click.option(
    "--prefix", help="src prefix to operate under", required=False, default=""
)

cascade_partial = partial(
    click.option,
    "--cascade/--no-cascade",
    "-c/",
    required=False,
    help="cascading search",
)
cascade = cascade_partial(default=True)
no_cascade = cascade_partial(default=False)

flat_output = click.option(
    "--flat-output",
    is_flag=True,
    show_default=True,
    default=False,
    help="flattens output of `/deeply/nested/paths` as simply `path`",
)
dirs_only = click.option(
    "--dirs-only",
    is_flag=True,
    show_default=True,
    default=False,
    help="returns directories only",
)
caller_context = click.option(
    "--caller-context",
    required=False,
    default=False,
    show_default=True,
    is_flag=True,
    help="display details about caller-context",
)

profile_partial = partial(
    click.option,
    "--profile",
    envvar="AWS_PROFILE",
    help="AWS profile to use",
)
src_profile_partial = partial(
    click.option,
    "--src-profile",
    help="Source Environment name",
    show_default=True,
)
dst_profile_partial = partial(
    click.option,
    "--dst-profile",
    help="Destination Environment name",
    show_default=True,
)

required_profile = profile_partial(
    required=True,
)
profile = default_profile = profile_partial(
    default="default",
    required=False,
)
src_profile = src_profile_default = src_profile_partial(
    default="default", required=False
)
dst_profile = dst_profile_default = dst_profile_partial(
    default="default", required=False
)
src_profile_no_default = src_profile_partial(default=None, required=False)
dst_profile_no_default = dst_profile_partial(default=None, required=False)

src_prefix = click.option(
    "--src-prefix",
    envvar="SRC_PREFIX",
    help="src prefix to operate under",
    required=False,
    default="",
)
