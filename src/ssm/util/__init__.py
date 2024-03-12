""" ssm.util
"""

import logging
import functools

import termcolor
import coloredlogs
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


def get_logger(name):
    """
    utility function for returning a logger
    with standard formatting patterns, etc
    """
    import os

    if os.path.exists(name):
        name = name.replace(os.path.expanduser("~/"), "")

    class DuplicateFilter(logging.Filter):
        def filter(self, record):
            # add other fields if you need more granular comparison, depends on your app
            current_log = (record.module, record.levelno, record.msg)
            if current_log != getattr(self, "last_log", None):
                self.last_log = current_log
                return True
            return False

    formatter = coloredlogs.ColoredFormatter(
        fmt=" - ".join(
            [
                # "[%(asctime)s]",
                "%(levelname)s\t",
                "%(name)s\t",
                "%(message)s",
            ]
        ),
        # datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    if not logger.handlers:
        # prevents duplicate registration
        logger.addHandler(log_handler)
    logger.addFilter(DuplicateFilter())  # add the filter to it
    # FIXME: get this from some kind of global config
    logger.setLevel("DEBUG")
    return logger


LOGGER = get_logger(__name__)
