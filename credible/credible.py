#!/usr/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import argparse
import os
import sys

# Since script is in package "credible" we can know what to add to path
(libpath,tail) = os.path.split(sys.path[0])
sys.path.append(libpath)
sys.path = sys.path[1:]

#print(libpath)
#print(tail)
#print(sys.path)

#from credible import core
from credible.core import SSCA, SSHKeyManager
#from credible.core import SSHKeyManager
# create the top-level parser
#parser = argparse.ArgumentParser(prog='PROG')
#parser.add_argument('--foo', action='store_true', help='foo help')
#subparsers = parser.add_subparsers(help='sub-command help')
# create the parser for the "a" command
#parser_a = subparsers.add_parser('a', help='a help')
#parser_a.add_argument('bar', type=int, help='bar help')
# create the parser for the "b" command
#parser_b = subparsers.add_parser('b', help='b help')
#parser_b.add_argument('--baz', choices='XYZ', help='baz help')

parser = argparse.ArgumentParser()

# Init sub-command
subparsers = parser.add_subparsers()
parser_init = subparsers.add_parser('hostcert', help='initialize the things')
parser_init = subparsers.add_parser('usercert', help='initialize the things')
parser_init = subparsers.add_parser('certchain', help='initialize the things')
parser_init = subparsers.add_parser('sshkey', help='initialize the things')
#parser_init.add_argument(...)


print("Credible!")
