""" ssm.cli.args (boilerplate for click)

    Common CLI arguments for reuse
"""

import click

secret_name = click.argument("secret_name", nargs=1)
path_prefix = click.argument("path_prefix", nargs=1)
namespace = click.argument("namespace", nargs=1)
path_prefix_default = click.argument("path_prefix", nargs=1, default="/")
