#!/bin/env python
#
# 
import sys
import re
import time
#from setuptools import setup
from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

def choose_data_file_locations():
    local_install = False

    if '--user' in sys.argv:
        local_install = True
    elif any([re.match('--home(=|\s)', arg) for arg in sys.argv]):
        local_install = True
    elif any([re.match('--prefix(=|\s)', arg) for arg in sys.argv]):
        local_install = True

    if local_install:
        return home_data_files
    else:
        return rpm_data_files

current_time = time.gmtime()
release_version = "{0}.{1:0>2}.{2:0>2}".format(current_time.tm_year, current_time.tm_mon, current_time.tm_mday)

etc_files = ['etc/autopyfactory-vc3config.conf',
             'etc/autopyfactory-wq.conf',
             'etc/mappings-wq.conf',
             'etc/monitor-wq.conf',
             'etc/queues-wq.conf',
             'etc/vc3defaults.conf',
             'etc/vc3authdefaults.conf',
            ]


rpm_data_files = [('/etc/autopyfactory', etc_files),
                 ]

home_data_files = [('etc', etc_files),
                  ]

data_files = choose_data_file_locations()

# ===========================================================

setup(
    name="vc3-factory-plugins",
    version=release_version,
    description='vc3-factory-plugins package',
    long_description='''This package contains the AutoPyFactory plugins for VC3''',
    license='GPL',
    author='Jose Caballero',
    author_email='jcaballero@bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='https://github.com/vc3-project',
    packages=['autopyfactory',
              'autopyfactory.plugins',
              'autopyfactory.plugins.factory',
              'autopyfactory.plugins.factory.config',
              'autopyfactory.plugins.factory.config.auth',
              'autopyfactory.plugins.factory.config.queues',
              'autopyfactory.plugins.factory.monitor',
              'autopyfactory.plugins.queue',
              'autopyfactory.plugins.queue.batchsubmit',
              'autopyfactory.plugins.queue.sched',
              'autopyfactory.plugins.queue.wmsstatus',
              ],
    data_files=data_files,
    install_requires=['autopyfactory']
)
