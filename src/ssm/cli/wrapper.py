""" ssm.cli.wrapper (click boilerplate)
    Reusable wrapper for building CLIs
"""

import functools
import json
import typing

import click
import yaml

from ssm import abcs, util

__all__ = ["ApiWrapper"]

LOGGER = util.get_logger(__file__)


class ApiWrapper(abcs.Loggable):
    """
    A wrapper that turns an API function into a Click CLI subcommand.

    Automatically handles:
    - Output formatting (json, yaml, env, stdout, tree)
    - Debug mode (--debug flag)
    - Quiet mode (--quiet flag)
    - Command aliasing
    """

    BASE_OPTIONS = [
        click.option(
            "--debug",
            default=False,
            is_flag=True,
            help="Enable verbose debug output.",
        ),
        click.option(
            "--quiet",
            "-q",
            default=False,
            is_flag=True,
            help="Suppress non-essential output.",
        ),
    ]

    def __init__(
        self,
        command_name: typing.Optional[str] = None,
        publishers: typing.List = None,
        subcommand_name: typing.Optional[str] = None,
        fxn: typing.Callable = None,
        extra_options: typing.List = None,
        aliases: typing.List[str] = None,
        help: typing.Optional[str] = None,
        entry=None,
    ):
        publishers = publishers or []
        aliases = aliases or []
        extra_options = extra_options or []

        self.entry = entry
        self.aliases = aliases
        self.is_subcommand = isinstance(self.entry, click.core.Group)
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
                f"command, got {self.entry} of type {type(self.entry)} for entry"
            )
            raise ValueError(err)
        super().__init__()

    def get_proxy(self):
        """Create the proxy function that wraps the API function."""
        options = self.extra_options.copy()
        if self.is_subcommand:
            # otherwise base options would be added twice for stand-alone style CLIs
            options += self.__class__.BASE_OPTIONS

        @functools.wraps(self.fxn)
        def proxy(*args, **kwargs):
            """Proxy function that handles debug/quiet modes and output formatting."""
            args = [x for x in args if not isinstance(x, click.core.Context)]

            # Handle debug mode
            debug = kwargs.pop("debug", False)
            if debug:
                util.set_log_level("DEBUG")

            # Handle quiet mode
            quiet = kwargs.pop("quiet", False)
            if quiet:
                util.set_log_level("ERROR")

            output_format = kwargs.get("format", "stdout")
            result = self.fxn(*args, **kwargs)

            # In quiet mode, only output if there's a result and it's not a success bool
            if quiet and (result is True or result is None):
                return

            self._format_output(result, output_format, quiet)

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
            err = f"unknown entry type '{type(self.entry)}' for '{self.entry}'"
            LOGGER.critical(err)
            raise RuntimeError(err)
        return result

    def _format_output(
        self, result: typing.Any, output_format: str, quiet: bool = False
    ) -> None:
        """Format and print the result based on the output format."""
        if result is None:
            return

        if output_format in ["yaml", "yml"]:
            print(yaml.dump(result, default_flow_style=False))
        elif output_format == "json":
            print(json.dumps(result, indent=2, default=str))
        elif output_format == "python":
            print(result)
        elif output_format == "env":
            if not isinstance(result, dict):
                raise ValueError(f"env format requires dict, got {type(result)}")
            acc = []
            for k, v in result.items():
                if isinstance(v, str) and " " in v:
                    LOGGER.warning(
                        "env format value contains space - may cause issues"
                    )
                tmp = "=".join([k.split("/")[-1], str(v)])
                acc.append(tmp)
            print("\n".join(acc))
        elif output_format in ["stdout", "tree"]:
            if isinstance(result, list):
                for item in result:
                    print(str(item))
            elif isinstance(result, dict):
                tree = util.Tree("", guide_style="bold bright_blue")
                util.rich_walk_dict(result, tree)
                util.rich_print(tree)
            elif isinstance(result, bool):
                # Don't print True/False for success indicators
                if not result:
                    print("Operation failed")
            else:
                util.rich_print(result)
        else:
            raise RuntimeError(f"unrecognized output format `{output_format}`")
