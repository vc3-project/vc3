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
import logging
import os
import sys
from ConfigParser import ConfigParser

# Since script is in package "credible" we can know what to add to path
#(libpath,tail) = os.path.split(sys.path[0])
#sys.path.append(libpath)
#sys.path = sys.path[1:]

from credible.core import SSCA, SSHKeyManager

class CredibleCLI(object):
    
    def __init__(self):
        self.parseopts()
        self.setuplogging()
                
        
    def setuplogging(self):
        self.log = logging.getLogger()
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        #formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.StreamHandler()
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
    
        self.log.setLevel(logging.WARN)
        if self.results.debug:
            self.log.setLevel(logging.DEBUG)
        # adding a new Handler for the console, 
        # to be used only for DEBUG and INFO modes. 
        #if self.options.logLevel in [logging.DEBUG, logging.INFO]:
        #    if self.options.console:
        #        console = logging.StreamHandler(sys.stdout)
        #        console.setFormatter(formatter)
        #        console.setLevel(self.options.logLevel)
        #        self.log.addHandler(console)
        #self.log.setLevel(self.options.logLevel)
        self.log.info('Logging initialized.')


    def parseopts(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', 
                            action="store", 
                            dest='configpath', 
                            default='~/etc/credible.conf', 
                            help='configuration file path.')
        
        parser.add_argument('-d', '--debug', 
                            action="store_true", 
                            dest='debug', 
                            help='debug logging')        
        
        # Init sub-command
        subparsers = parser.add_subparsers( dest="subcommand")
        
        parser_hostcert = subparsers.add_parser('hostcert', 
                                                help='generate/retrieve hostcert')
        parser_hostcert.add_argument('-C','--caname', 
                                     action="store", 
                                     dest="caname", 
                                     default='defaultca')
        parser_hostcert.add_argument('hostname', 
                                     action="store")
        
        parser_hostkey = subparsers.add_parser('hostkey', 
                                                help='generate/retrieve hostkey')
        parser_hostkey.add_argument('-C','--caname', 
                                     action="store", 
                                     dest="caname", 
                                     default='defaultca')
        parser_hostkey.add_argument('hostname', 
                                     action="store")
        
        parser_usercert = subparsers.add_parser('usercert', 
                                                help='generate/retrieve user cert.')
        parser_usercert.add_argument('-C','--caname', 
                                     action="store", 
                                     dest="caname", 
                                     default='defaultca')
        parser_usercert.add_argument('subject', action="store")
        
        
        parser_userkey = subparsers.add_parser('userkey', 
                                                help='generate/retrieve user key.')
        parser_userkey.add_argument('-C','--caname', 
                                     action="store", 
                                     dest="caname", 
                                     default='defaultca')
        parser_userkey.add_argument('subject', action="store")
                
        
        
        parser_certchain = subparsers.add_parser('certchain', 
                                                 help='return certificate chain.')
        parser_certchain.add_argument('-C', '--caname', 
                                      action="store", 
                                      dest="caname", 
                                      default='defaultca',
                                      help='label for certificate authority')
        
        parser_sshpubkey = subparsers.add_parser('sshpubkey', 
                                              help='generate retrieve SSH public key')
        parser_sshpubkey.add_argument('-s', '--storename', 
                                      action="store", 
                                      dest="sshname", 
                                      default='sshdefault',
                                      help='label for SSH group')
        parser_sshpubkey.add_argument('principal', 
                                   action="store",
                                   help='SSH username/identifier')
        
        parser_sshprivkey = subparsers.add_parser('sshprivkey', 
                                              help='generate retrieve SSH private key')
        parser_sshprivkey.add_argument('-s', '--storename', 
                                      action="store", 
                                      dest="sshname", 
                                      default='sshdefault',
                                      help='label for SSH group')
        parser_sshprivkey.add_argument('principal', 
                                   action="store",
                                   help='SSH username/identifier')
        
        
        
        self.results= parser.parse_args()
        print(self.results)

    def invoke(self):
        cp = ConfigParser()
        ns = self.results
        self.log.info("Config is %s" % ns.configpath)
        cp.read(os.path.expanduser(ns.configpath))
        
        if ns.subcommand == 'hostcert':
            ssca = SSCA( cp, ns.caname)
            (c,k) = ssca.gethostcert(ns.hostname)
            print(c) 

        if ns.subcommand == 'hostkey':
            ssca = SSCA( cp, ns.caname)
            (c,k) = ssca.gethostcert(ns.hostname)
            print(k) 

        if ns.subcommand == 'usercert':
            ssca = SSCA( cp, ns.caname)
            (c,k) = ssca.getusercert(ns.subject)
            print(c) 

        if ns.subcommand == 'userkey':
            ssca = SSCA( cp, ns.caname)
            (c,k) = ssca.getusercert(ns.subject)
            print(k) 

        if ns.subcommand == 'certchain':
            ssca = SSCA( cp, ns.caname)
            cc = ssca.getcertchain()
            print(cc)    
                
        if ns.subcommand == 'sshpubkey':
            sska = SSHKeyManager(cp, ns.sshname)
            (pub,priv) = sska.getkeys(ns.principal)
            print(pub)

        if ns.subcommand == 'sshprivkey':
            sska = SSHKeyManager(cp, ns.sshname)
            (pub,priv) = sska.getkeys(ns.principal)
            print(priv)
    
        #self.log.debug("Running...")
        
        

if __name__ == '__main__':
    ccli = CredibleCLI()
    ccli.invoke()

