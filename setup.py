#!/usr/bin/env python
#
# Setup prog for vc3-client
#
#

import sys
import re
from setuptools import setup
import time


def choose_data_file_locations():
    local_install = False

    if '--user' in sys.argv:
        local_install = True
    elif any( [ re.match('--home(=|\s)', arg) for arg in sys.argv] ):
        local_install = True
    elif any( [ re.match('--prefix(=|\s)', arg) for arg in sys.argv] ):
        local_install = True

    if local_install:
        return home_data_files
    else:
        return rpm_data_files

current_time = time.gmtime()
#release_version = "{0}.{1:0>2}.{2:0>2}".format(current_time.tm_year, current_time.tm_mon, current_time.tm_mday)
release_version='1.1.0'

scripts   = ['scripts/vc3-client', ]
etc_files = ['etc/vc3-client.conf']

rpm_data_files  = [('/etc/vc3', etc_files),]
home_data_files = [('etc', etc_files),]
data_files      = choose_data_file_locations()

# ===========================================================

# setup for distutils
print(scripts)
setup(
    name="vc3-client",
    version=release_version,
    description='vc3-client package',
    long_description='''This package contains vc3 client''',
    license='GPL',
    author='VC3 Team',
    author_email='vc3-project@googlegroups.com',
    maintainer='VC3 team',
    maintainer_email='vc3-project@googlegroups.com',
    url='http://virtualclusters.org/',
    packages=['vc3client'],
    scripts=scripts,
    data_files=data_files,
    install_requires=['requests', 'pyopenssl', 'cherrypy', 'pyyaml', 'vc3-infoservice']
)


