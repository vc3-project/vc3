#!/usr/bin/env python
#
# Setup prog for plugins-management
#

import os
import re
import sys

from setuptools import setup

import pluginmanager
release_version = pluginmanager.__version__

# setup for distutils
setup(
    name="pluginmanager",
    version=release_version,
    description='plugin-manager package',
    long_description='''This package contains the plugins management''',
    license='GPL',
    author='Jose Caballero',
    author_email='jcaballero@bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='https://github.com/bnl-sdcc/plugin-manager',
    py_modules=['pluginmanager', ],
    scripts = [ ],
    data_files = []
)
