# -*- coding: utf-8 -*-
""" ssm.cli.options (boilerplate for click)

    Common CLI arguments for reuse
"""
from __future__ import absolute_import

from functools import partial

import click

cluster = click.option(
    '--cluster',
    required=False,default='',
    help='cluster to use (defaults to autodetection from env)')
comment = click.option('--comment', help='comment or description', required=False)
container = click.option('--container', help='container to enter', required=False)
key = click.option('--key', help='key to use', default='', required=False)

top = click.option(
    '--top', help='triage and only describe top N results',
    required=False)
existing_file = click.option(
    '--file', type=click.Path(exists=True))
filter_service_partial = partial(click.option,
                                 '--service', help='filter for service',
                                 required=False)
filter_service = filter_service_partial(default='.*')

file_format_partial = partial(click.option,
    '--format', type=click.Choice(['json', 'yaml', 'yml', 'env']),
    help='file format', )
file_format = format = file_format_partial(required=True)
file_format_yml_default = file_format_yaml_default = file_format_partial(required=False,default='yaml')
required_dest_bucket = dest_bucket = click.option(
    '--dest-bucket', envvar='DEST_BUCKET',
    help='dest bucket name', required=True)


optional_user = user = click.option('--user', help='username (default will attempt auto-detect)', required=False, default='')
optional_users = users = click.option('--users', help='user list (comma-separatted)', required=False, default='')
optional_database = database = click.option('--database', help='database (default will attempt auto-detect)', required=False, default='')

required_bucket = click.option(
    '--bucket', help='bucket name', required=True)

raw = click.option(
    '--raw', '-r', help='unquotes text return values (like jq -r)',
    default=False)

force_or_dry = force = dry_run = click.option(
    '--force/--dry-run', '-f/-d', help='perform actions',
    default=False, envvar='FORCE')

pause_or_nowait = no_wait = pause = click.option(
    '--pause/--no-wait', help='pause before starting',
    default=True)

optional_prefix = click.option(
    '--prefix', help='src prefix to operate under',
    required=False, default='')

dest_prefix = click.option(
    '--dest-prefix', envvar='DEST_PREFIX',
    help='dest prefix to operate under',
    required=False, default='')

required_user = click.option(
    '--user', help='username to use', required=True, default='')

optional_src_bucket = click.option(
    '--src-bucket', envvar='SRC_BUCKET',
    help='src bucket name', required=False)

required_src_bucket = click.option(
    '--src-bucket', envvar='SRC_BUCKET',
    help='src bucket name', required=True)

command = click.option(
    '--command', '-c', required=False, default='',
    help='Command to run (like bash -c)', )
required_command = click.option(
    '--command', '-c', default='',
    help='Command to run (like bash -c)', )

script = click.option(
    '--script', '-s', help='Script to run', default='')

cascade_partial = partial(
    click.option,
    '--cascade/--no-cascade', '-c/',
    required=False, help='cascading search')
cascade = cascade_partial(default=True)
no_cascade = cascade_partial(default=False)

no_cascade = click.option(
    '--no-cascade', required=False, default=False, flag=True,
    help='regex to filter results by', )

filter = click.option(
    '--filter', required=False, default='.*',
    help='regex to filter results by', )

optional_arn = click.option(
    '--arn', required=False, default='',
    help='ARN', )
optional_role_name = click.option(
    '--role-name', required=False, default='',
    help='Role name', )

env_partial = partial(
    click.option, '--env', envvar='AWS_PROFILE',
        help='Environment to use',)
src_env_partial = partial(
    click.option, '--src-env',
    help='Source Environment name',)
dest_env_partial = partial(
    click.option, '--dest-env',
    help='Destination Environment name',)

required_env = env_partial(required=True,)
optional_env = env_no_default = env_partial(required=False,)
env = default_env = env_partial(default='default', required=False, )
src_env = src_env_default = src_env_partial(default='default', required=False)
dest_env = dest_env_default = dest_env_partial(default='default', required=False)
src_env_no_default = src_env_partial(default=None, required=False)
dest_env_no_default  = dest_env_partial(default=None, required=False)

required_stack = click.option(
    '--stack', required=True, help='Stack name to use',)

required_key = click.option(
    '--key', required=True, help='Key name to use',)

src_prefix = click.option(
    '--src-prefix', envvar='SRC_PREFIX',
    help='src prefix to operate under',
    required=False, default='')

required_regexp = click.option(
    '--regexp', required=True,
    help='RegExp to use',)
