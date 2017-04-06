#!/usr/bin/env python
#
# Setup prog for plugins-management
#
#

import commands
import os
import re
import sys

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

import pluginmanager
release_version = pluginmanager.__version__

# setup for distutils
setup(
    name="plugin-manager",
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
