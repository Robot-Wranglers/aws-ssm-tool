""" ssm.util

Utility functions for logging, formatting, and output.
"""

import logging
import os
import typing

from rich import print as rich_print  # noqa
from rich.console import Console
from rich.default_styles import DEFAULT_STYLES
from rich.logging import RichHandler
from rich.style import Style
from rich.text import Text
from rich.theme import Theme
from rich.tree import Tree

__all__ = [
    "get_logger",
    "set_log_level",
    "is_string",
    "flatten_output",
    "fatal_error",
    "rich_walk_dict",
    "rich_print",
    "Tree",
    "CONSOLE",
]

# Global log level - can be set via SSM_LOG_LEVEL env var or set_log_level()
_LOG_LEVEL = os.environ.get("SSM_LOG_LEVEL", "WARNING").upper()


def set_log_level(level: str) -> None:
    """
    Set global log level for all SSM loggers.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _LOG_LEVEL
    _LOG_LEVEL = level.upper()
    # Update existing loggers
    for name in logging.Logger.manager.loggerDict:
        if name.startswith("ssm"):
            logging.getLogger(name).setLevel(_LOG_LEVEL)


def rich_walk_dict(
    dct: dict, tree: Tree, branch_color: str = "[bold magenta]"
) -> None:
    """Recursively build rich.tree.Tree from dict contents."""
    for k, v in dct.items():
        if isinstance(v, dict):
            style = "dim"
            branch = tree.add(
                f"{branch_color}{k}",
                style=style,
                guide_style=style,
            )
            rich_walk_dict(v, branch)
        else:
            tree.add(Text(f"{k}", "green") + Text(": ") + Text(f"{v}"))


def is_string(obj: typing.Any) -> bool:
    """Check if object is a string."""
    return isinstance(obj, str)


def flatten_output(result: dict) -> dict:
    """Flatten nested path keys to just the final component."""
    acc = {}
    for k, v in result.items():
        tmp = k.split("/")
        acc[tmp[-1]] = v
    return acc


def fatal_error(msg: str) -> typing.NoReturn:
    """Log error and exit."""
    LOGGER.error(f"error: {msg}")
    raise SystemExit(1)


class Fake:
    """Fake Logger Object for silent operation."""

    def warning(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


THEME = Theme(
    {
        **DEFAULT_STYLES,
        **{
            "logging.keyword": Style(bold=True, color="yellow"),
            "logging.level.debug": Style(color="green"),
            "logging.level.info": Style(dim=True),
            "logging.level.warning": Style(color="yellow"),
            "logging.level.error": Style(color="red", dim=True, bold=True),
            "logging.level.critical": Style(color="red", bold=True),
            "log.level": Style.null(),
            "log.time": Style(color="cyan", dim=True),
            "log.message": Style.null(),
            "log.path": Style(dim=True),
        },
    }
)
CONSOLE = Console(theme=THEME, stderr=True)

# Track if basicConfig has been called to avoid duplicate handlers
_logging_configured = False


def get_logger(
    name: str,
    console: Console = CONSOLE,
    fake: bool = False,
) -> logging.Logger:
    """
    Get a logger with standard formatting.

    Args:
        name: Logger name (typically __name__)
        console: Rich console for output
        fake: If True, return a silent fake logger

    Returns:
        Configured logger instance

    Environment:
        SSM_LOG_LEVEL: Set default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    global _logging_configured

    if fake:
        return Fake()

    if not _logging_configured:
        log_handler = RichHandler(
            rich_tracebacks=True,
            console=console,
            show_time=False,
        )

        logging.basicConfig(
            format="%(message)s",
            datefmt="[%X]",
            handlers=[log_handler],
            level=_LOG_LEVEL,
        )

        formatter = logging.Formatter(
            fmt="%(name)s %(message)s",
            datefmt="",
        )
        log_handler.setFormatter(formatter)
        _logging_configured = True

    logger = logging.getLogger(name)
    logger.setLevel(_LOG_LEVEL)

    return logger


LOGGER = get_logger(__name__)
