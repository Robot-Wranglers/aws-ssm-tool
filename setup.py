#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'ssm'

setup(
    name=PACKAGE_NAME,
    version='0.1',
    author="robot-wranglers",
    description="",
    author_email='admin@example.com',
    url='https://github.com/robot-wranglers/ssm',
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    dependency_links=[
    ],
    entry_points={
        'console_scripts':
        [
            'ssm = {0}.bin.ssm:entry'.format(PACKAGE_NAME),
        ]},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
