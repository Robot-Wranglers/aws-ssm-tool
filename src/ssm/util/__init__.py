""" ssm.util
"""

import logging
import functools

import termcolor
from rich.text import Text
from rich.tree import Tree

from rich import print as rich_print  # noqa

blue = functools.partial(termcolor.colored, color="blue")
red = functools.partial(termcolor.colored, color="red")
green = functools.partial(termcolor.colored, color="green")
yellow = functools.partial(termcolor.colored, color="yellow")
bold = functools.partial(termcolor.colored, attrs=["bold"])


def rich_walk_dict(dct, tree: Tree, branch_color="[bold magenta]") -> None:
    """recursively build rich.tree.Tree from dict contents"""
    for k, v in dct.items():
        if isinstance(v, (dict,)):
            style = "dim"
            branch = tree.add(
                f"{branch_color}{k}",
                style=style,
                guide_style=style,
            )
            rich_walk_dict(v, branch)
        else:
            tree.add(Text(f"{k}", "green") + Text(": ") + Text(f"{v}"))


def is_string(obj) -> bool:
    """ """
    return isinstance(obj, str)


def flatten_output(result: dict) -> dict:
    """ """
    acc = {}
    for k, v in result.items():
        tmp = k.split("/")
        acc[tmp[-1]] = v
    return acc


def fatal_error(msg):
    """ """
    LOGGER.info("{} {}".format(red("error:"), msg))
    raise SystemExit(1)


from rich.style import Style
from rich.theme import Theme
from rich.console import Console
from rich.logging import RichHandler
from rich.default_styles import DEFAULT_STYLES


class Fake:
    warning = debug = info = critical = lambda *args, **kwargs: None
    # if isinstance(handler, type(logging.StreamHandler())):
    #     handler.setLevel(logging.DEBUG)
    #     logger.debug('Debug logging enabled')


THEME = Theme(
    {
        **DEFAULT_STYLES,
        **{
            "logging.keyword": Style(bold=True, color="yellow"),
            # "logging.level.notset": Style(dim=True),
            "logging.level.debug": Style(color="green"),
            "logging.level.info": Style(
                dim=True,
                # color="blue",
            ),
            "logging.level.warning": Style(color="yellow"),
            "logging.level.error": Style(color="red", dim=True, bold=True),
            "logging.level.critical": Style(
                color="red",
                bold=True,
                # reverse=True
            ),
            "log.level": Style.null(),
            "log.time": Style(color="cyan", dim=True),
            "log.message": Style.null(),
            "log.path": Style(dim=True),
        },
    }
)
CONSOLE = Console(theme=THEME, stderr=True)


def get_logger(name, console=CONSOLE, fake=False):
    """utility function for returning a logger
    with standard formatting patterns, etc

    :param name: param console:  (Default value = CONSOLE)
    :param console:  (Default value = CONSOLE)

    """
    if fake:
        return Fake()
    log_handler = RichHandler(
        rich_tracebacks=True,
        console=console,
        show_time=False,
    )

    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[log_handler],
    )
    FormatterClass = logging.Formatter
    formatter = FormatterClass(
        fmt=" ".join(["%(name)s", "%(message)s"]),
        # datefmt="%Y-%m-%d %H:%M:%S",
        datefmt="",
    )
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # FIXME: get this from some kind of global config
    logger.setLevel("DEBUG")

    return logger


LOGGER = get_logger(__name__)
