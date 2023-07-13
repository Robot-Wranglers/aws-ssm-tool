"""
See the docs here:
  https://github.com/elo-enterprises/aws-secrets
"""


import functools

import click

from ssm import api, cli, util

LOGGER = util.get_logger(__name__)


@click.command(cls=cli.Group)
def entry(*args, **kargs):  # noqa
    """
    Tool for accessing secrets
    """
    # this could update global settings here
    # ctx = {}
    # ctx['verbose'] = verbose
    # for key, value in config:
    #     ctx[key] = value


ApiWrapper = functools.partial(
    cli.ApiWrapper,
    entry=entry,
)

list = ApiWrapper(
    fxn=api.list,
    aliases=["ls"],
    extra_options=[
        cli.options.env,
        cli.args.secret_name,
    ],
)

read = ApiWrapper(
    fxn=api.read,
    aliases=["get"],
    extra_options=[
        cli.options.env,
        cli.options.cascade,
        cli.args.secret_name,
    ],
)

delete = ApiWrapper(
    fxn=api.delete,
    aliases=[
        "rm",
    ],
    extra_options=[
        cli.options.env,
        cli.args.secret_name,
        click.option(
            "--no-backup",
            help="do not create backup file",
            is_flag=True,
            default=False,
            required=False,
        ),
    ],
)

move = ApiWrapper(
    fxn=api.move,
    aliases=["mv"],
    extra_options=[
        cli.options.src_env_default,
        cli.options.dest_env_default,
        click.argument("dest_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)
move_many = ApiWrapper(
    fxn=api.move_many,
    aliases=["mv-many", "move-path", "mv-path"],
    extra_options=[
        cli.options.src_env_default,
        cli.options.dest_env_default,
        click.argument("dest_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)
copy = ApiWrapper(
    fxn=api.copy,
    aliases=["cp"],
    extra_options=[
        cli.options.src_env_default,
        cli.options.dest_env_default,
        click.argument("dest_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)
update = ApiWrapper(
    fxn=api.update,
    aliases=["put", "set"],
    extra_options=[
        cli.options.env,
        cli.options.existing_file,
        click.argument("value", default="", nargs=1),
        cli.args.secret_name,
    ],
)
get_many = ApiWrapper(
    fxn=api.get_many,
    aliases=["get-path"],
    extra_options=[
        cli.options.env,
        cli.options.cascade,
        cli.options.file_format,
        cli.args.namespace,
    ],
)
put_many = ApiWrapper(
    fxn=api.put_many,
    aliases=["put-path"],
    extra_options=[
        cli.options.env,
        cli.options.file_format_yaml_default,
        cli.args.namespace,
    ],
)
