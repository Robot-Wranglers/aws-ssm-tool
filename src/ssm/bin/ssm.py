""" ssm.bin.ssm

  Command-line entry-points.  
  (This file makes parts of `ssm.api` available via click)
"""

import functools

import click

from ssm import api, cli, util
from ssm.cli.wrapper import ApiWrapper

LOGGER = util.get_logger(__name__)


@click.command(cls=cli.Group)
def entry(*args, **kargs):  # noqa
    """
    SSM tool, a small helper for interacting with Amazon Simple Systems Manager
    for secrets storage/retrieval.
    """
    # this could update global settings here
    # ctx = {}
    # ctx['verbose'] = verbose
    # for key, value in config:
    #     ctx[key] = value


ApiWrapper = functools.partial(
    ApiWrapper,
    entry=entry,
)

list = ApiWrapper(
    fxn=api.list,
    aliases=["ls"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_tree_default,
        cli.options.dirs_only,
        click.argument("path_prefix", nargs=1, default="/"),
    ],
)

list_dirs = ApiWrapper(
    fxn=api.list_dirs,
    aliases=["ls-dirs"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        click.argument("path_prefix", nargs=1, default="/"),
    ],
)

stat = ApiWrapper(
    fxn=api.stat,
    aliases=["st"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_stdout_default,
        cli.options.caller_context,
        click.argument("path_prefix", nargs=1, default="/"),
    ],
)

read = ApiWrapper(
    fxn=api.read,
    aliases=["get"],
    extra_options=[
        cli.options.profile,
        cli.args.secret_name,
    ],
)

delete = ApiWrapper(
    fxn=api.delete,
    aliases=[
        "rm",
    ],
    extra_options=[
        cli.options.profile,
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
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        click.argument("dst_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)

move_many = ApiWrapper(
    fxn=api.move_many,
    aliases=["mv-many", "move-path", "mv-path"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        click.argument("dst_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)

copy = ApiWrapper(
    fxn=api.copy,
    aliases=["cp"],
    extra_options=[
        cli.options.src_profile_default,
        cli.options.dst_profile_default,
        click.argument("dst_name", nargs=1),
        click.argument("src_name", nargs=1),
    ],
)

update = ApiWrapper(
    fxn=api.update,
    aliases=["put", "set"],
    extra_options=[
        cli.options.profile,
        cli.options.existing_file,
        click.argument("value", default="", nargs=1),
        cli.args.secret_name,
    ],
)

get_many = ApiWrapper(
    fxn=api.get_many,
    aliases=["get-path"],
    extra_options=[
        cli.options.profile,
        cli.options.cascade,
        cli.options.flat_output,
        cli.options.output_format_yaml_default,
        cli.args.namespace,
    ],
)

put_many = ApiWrapper(
    fxn=api.put_many,
    aliases=["put-path"],
    extra_options=[
        cli.options.profile,
        cli.options.output_format_yaml_default,
        cli.args.namespace,
    ],
)
