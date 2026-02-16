""" ssm.cli.args (boilerplate for click)

    Common CLI arguments for reuse across commands.
"""

import click

from ssm.cli import completion

__all__ = ["secret_name", "path_prefix", "namespace"]

secret_name = click.argument(
    "secret_name", nargs=1, shell_complete=completion.complete_parameters
)
path_prefix = click.argument(
    "path_prefix", nargs=1, shell_complete=completion.complete_paths
)
namespace = click.argument(
    "namespace", nargs=1, shell_complete=completion.complete_paths
)
