""" ssm.cli.args (boilerplate for click)

    Common CLI arguments for reuse
"""

import click

secret_name = click.argument("secret_name", nargs=1)
namespace = click.argument("namespace", nargs=1)
