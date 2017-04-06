#!/usr/bin/env python
#
# Setup prog for Certify certificate management utility

import sys
from distutils.core import setup

from credible import core
release_version=core.__version__

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
             ]

)


