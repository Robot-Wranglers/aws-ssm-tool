""" ssm.cli.options (boilerplate for click)

    Common CLI options for reuse across commands.
"""

from functools import partial

import click

from ssm.cli import completion

__all__ = [
    "profile",
    "src_profile",
    "src_profile_default",
    "dst_profile",
    "dst_profile_default",
    "output_format",
    "output_format_yaml_default",
    "output_format_stdout_default",
    "output_format_tree_default",
    "existing_file",
    "flat_output",
    "dirs_only",
    "caller_context",
]

# === FILE OPTIONS ===

existing_file = click.option(
    "--file",
    "file",
    type=click.Path(exists=True),
    help="Path to input file.",
)

# === OUTPUT FORMAT OPTIONS ===

output_format_partial = partial(
    click.option,
    "--format",
    show_default=True,
    type=click.Choice(["json", "yaml", "yml", "env", "stdout", "tree"]),
    help="Output format.",
)
output_format = output_format_partial(required=True)
output_format_yaml_default = output_format_partial(required=False, default="yaml")
output_format_json_default = output_format_partial(required=False, default="json")
output_format_stdout_default = output_format_partial(required=False, default="stdout")
output_format_tree_default = output_format_partial(required=False, default="tree")

# === OUTPUT MODIFIER OPTIONS ===

flat_output = click.option(
    "--flat-output",
    is_flag=True,
    show_default=True,
    default=False,
    help="Flatten output paths to just the final component.",
)

dirs_only = click.option(
    "--dirs-only",
    is_flag=True,
    show_default=True,
    default=False,
    help="Return directories only, not leaf parameters.",
)

caller_context = click.option(
    "--caller-context",
    required=False,
    default=False,
    show_default=True,
    is_flag=True,
    help="Include AWS caller identity in output.",
)

# === PROFILE OPTIONS ===

profile_partial = partial(
    click.option,
    "--profile",
    envvar="AWS_PROFILE",
    help="AWS profile to use.",
    shell_complete=completion.complete_profiles,
)

src_profile_partial = partial(
    click.option,
    "--src-profile",
    help="Source AWS profile.",
    show_default=True,
    shell_complete=completion.complete_profiles,
)

dst_profile_partial = partial(
    click.option,
    "--dst-profile",
    help="Destination AWS profile.",
    show_default=True,
    shell_complete=completion.complete_profiles,
)

profile = profile_partial(
    default="default",
    required=False,
)

src_profile = src_profile_default = src_profile_partial(
    default="default",
    required=False,
)

dst_profile = dst_profile_default = dst_profile_partial(
    default="default",
    required=False,
)
