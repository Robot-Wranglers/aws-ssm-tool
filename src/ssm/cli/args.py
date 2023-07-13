# -*- coding: utf-8 -*-
""" ssm.cli.args (boilerplate for click)

    Common CLI arguments for reuse
"""
from __future__ import absolute_import
import click
from functools import partial

secret_name = click.argument('secret_name', nargs=1)
namespace = click.argument('namespace', nargs=1)
