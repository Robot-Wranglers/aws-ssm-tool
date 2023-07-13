""" ssm.cli (click boilerplate)
"""

import click
from . import options, args # noqa

from ssm import util
LOGGER = util.get_logger(__name__)


class Group(click.Group):
    """
    Subclass of click.Group, mostly just for supporting command aliases
    """

    def list_commands(self, ctx):
        """
        Override  from super.

        This just re-orders aliases to the bottom of --help
        """
        result = click.Group.list_commands(self, ctx)
        root_commands = [x for x in result if not self.commands[x].is_alias]
        alias_commands = [x for x in result if self.commands[x].is_alias]
        result = root_commands + alias_commands
        return result

    def command(self, *args, **kwargs):
        """
        Override  from super.
        """
        aliases = kwargs.pop("aliases", [])

        def decorator(f):
            cmd = click.decorators.command(*args, **kwargs)(click.pass_context(f))
            self.add_command(cmd)
            cmd.is_alias = False
            for alias in aliases:
                zz = kwargs.copy()

                def g(*aa, **kk):
                    return f(*aa, **kk)

                g.__doc__ = g.help = f"ALIAS for `{cmd.name}`"
                zz.update(help=f"ALIAS for `{cmd.name}`")
                alias_cmd = click.decorators.command(**zz)
                alias_cmd = alias_cmd(click.pass_context(g))
                alias_cmd.params = cmd.params
                self.add_command(alias_cmd, name=alias)
                alias_cmd.is_alias = True
            return cmd

        return decorator
