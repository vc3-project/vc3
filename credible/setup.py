#!/usr/bin/env python
#
# Setup prog for Certify certificate management utility

import sys
from distutils.core import setup

from credible import core
release_version=core.__version__

# ===========================================================
#                D A T A     F I L E S
# ===========================================================

etc_files = [ 'etc/credible.conf',
              'etc/credible.conf.sample',
              'etc/openssl.cnf.intermediate.template',
              'etc/openssl.cnf.root.template',
            ]

home_data_files = [
            ('etc', etc_files)
            ]

rpm_data_files= [
            ('/etc/credible', etc_files)
            ]

def choose_data_files():
    rpminstall = True
    userinstall = False

    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True

    if rpminstall:
        return rpm_data_files
    elif userinstall:
        return home_data_files
    else:
        # Something probably went wrong, so punt
        return rpm_data_files

setup(
    name="credible",
    version=release_version,
    description='Utility for generating SSL host and user certs and SSH keypairs',
    long_description='''Utility for generating SSL host and user certs and SSH keypairs''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://www.racf.bnl.gov/experiments/usatlas/griddev/',
    packages=[ 'credible',
               'credible.plugins'
              ],
    classifiers=[
          'Development Status :: 3 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GPL',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System Administration :: Management',
    ],
    scripts=[ 'scripts/credible',
             ],
    data_files = choose_data_files()
)
