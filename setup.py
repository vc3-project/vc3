#!/usr/bin/env python
#
# Setup prog for Certify certificate management utility

import sys
from distutils.core import setup

import glidein

release_version=glidein.__version__

setup(
    name="condor-glidein-wrapper",
    version=release_version,
    description='Simple condor glidein job script.',
    long_description='''Simple condor glidein job script.''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://www.racf.bnl.gov/experiments/usatlas/griddev/',
    py_modules=[ 'glidein',
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
    data_files=[ ('share/condor_glidein', 
                      ['README.txt',
                       'glidein.submit'
                        ]
                  ),
               ]
)

