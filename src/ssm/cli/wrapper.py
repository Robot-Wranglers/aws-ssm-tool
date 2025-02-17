""" ssm.cli.wrapper (click boilerplate)
    Reusable wrapper for building CLIs
"""

import json
import functools

import yaml
import click

from ssm import abcs, util

LOGGER = util.get_logger(__file__)


class ApiWrapper(abcs.Loggable):
    """
    a wrapper that turns a API function into a click CLI subcommand
    """

    BASE_OPTIONS = [
        # every command gets the --debug option
        click.option(
            "--debug",
            default=False,
            is_flag=True,
            help="Enables verbose mode.",
        ),
    ]

    def __init__(
        self,
        command_name=None,
        publishers=[],
        subcommand_name=None,
        fxn=None,
        extra_options=None,
        aliases=[],
        help=None,
        entry=None,
    ):
        self.entry = entry
        self.aliases = aliases
        self.is_subcommand = isinstance(self.entry, (click.core.Group,))
        self.is_stand_alone = self.entry is None
        self.subcommand_name = self.name = subcommand_name or fxn.__name__.replace(
            "_", "-"
        )
        self.command_name = command_name
        self.fxn = fxn
        self.fxn.publishers = getattr(self.fxn, "publishers", publishers)
        self.extra_options = extra_options
        default_help = "no docstring"
        self.help = help or getattr(fxn, "__doc__", default_help) or default_help
        self.help = self.help.strip()
        self.proxy = self.get_proxy()
        if not callable(self.proxy):
            err = f"Expected callable for proxy, got '{self.proxy}'"
            raise ValueError(err)
        if not (self.is_subcommand or self.is_stand_alone):
            err = (
                "expected a group or a standalone "
                "command, got {} of type {} for entry"
            )
            err = err.format(self.entry, type(self.entry))
            raise ValueError(err)
        super().__init__()

    def get_proxy(self):
        """ """
        options = self.extra_options
        if self.is_subcommand:
            # otherwise base options would be added twice for stand-alone style CLIs
            options += self.__class__.BASE_OPTIONS

        @functools.wraps(self.fxn)
        def proxy(*args, **kwargs):
            """ """
            args = [x for x in args if not isinstance(x, (click.core.Context,))]
            # LOGGER.info(f"proxying args={args}, kwargs={kwargs}")
            format = kwargs.get("format", "stdout")
            result = self.fxn(*args, **kwargs)
            if format in ["yaml", "yml"]:
                print(yaml.dump(result))
            elif format in ["json"]:
                print(json.dumps(result))
            elif format in ["python"]:
                print(result)
            elif format in ["env"]:
                assert isinstance(result, (dict,)), f"expected dict, got {type(result)}"
                acc = []
                for k, v in result.items():
                    if isinstance(v, (str,)) and " " in v:
                        msg = "user requested format is `env` but value has a space character!"
                        LOGGER.warning(msg)
                    tmp = "=".join([k.split("/")[-1], v])
                    acc.append(tmp)
                print("\n".join(acc))
            elif format in ["stdout", "tree"]:
                if isinstance(result, (type([]),)):
                    # if format=='tree':
                    #     tree={}
                    #     for path_prefix in result:
                    #         for comp in path_prefix.split('/'):
                    #             tree[path_prefix]=
                    # else:
                    print("\n".join([str(x) for x in result]))
                elif isinstance(result, (dict,)):
                    tree = util.Tree(
                        "",
                        guide_style="bold bright_blue",
                    )
                    util.rich_walk_dict(result, tree)
                    util.rich_print(tree)
                else:
                    util.rich_print(result)
            else:
                raise RuntimeError(f"unrecognized output format `{format}`")

        for option in options:
            proxy = option(proxy)

        if self.is_subcommand:
            if self.aliases:
                result = self.entry.command(
                    name=self.name, help=self.help, aliases=self.aliases
                )(proxy)
            else:
                result = self.entry.command(name=self.name, help=self.help)(proxy)
        elif self.entry is None:
            result = click.command()(proxy)
        else:
            err = "unknown entry type '{}' for '{}'".format(
                type(self.entry), self.entry
            )
            LOGGER.critical(err)
            raise RuntimeError(err)
        return result
