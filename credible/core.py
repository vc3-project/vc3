#!/usr/bin/env python 

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import logging
import os


from optparse import OptionParser
from ConfigParser import ConfigParser
from pluginmanager.plugin import PluginManager

class SSHKeyManager(object):
    '''
    Handles generation, storage, and retrieval of SSH keypairs. 
    
    '''    
    def __init__(self, name, config):
        self.name = name
        
    def genkeys(self):
        pubkey = "AAAAA"
        privkey = "BBBBB"
        return (pubkey, privkey)


class SSCA(object):
    '''
    Represents a Self-Signed Certificate authority. 
    '''
    
    def __init__(self, name, config):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.caname = name
        self.vardir = config.get('credible', 'vardir')
        self.roottemplate=config.get('credible-ssca', 'roottemplate')
        self.intermediatetemplate=config.get('credible-ssca', 'intermediatetemplate')
        self.country = config.get('credible-ssca', 'country')   
        self.state = config.get('credible-ssca', 'state')  
        self.locality = config.get('credible-ssca', 'locality')
        self.organization = config.get('credible-ssca', 'organization')
        self.orgunit = config.get('credible-ssca', 'orgunit')
        self.email = config.get('credible-ssca', 'email')
        self.log.info("SSCA [%s] initted" % self.caname) 

    def createroot(self):
        pass

    def createintermediate(self):
        pass
    
    def certchain(self):
        chain = 'XXXXAAAAFFFF'
        return chain     
    
    def hostcert(self, hostname):
        c = "ZZZZZZZ"
        k = "SSSSSSS"
        return (c,k)

    def usercert(self, hostname):
        c = "UUUUUUU"
        k = "PPPPPPP"
        return (c,k)
    
    

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    cf = os.path.expanduser("etc/credible.conf")
    cp = ConfigParser()
    cp.read(cf)
    ssca = SSCA('catest', cp)
    ssca.createroot()
    ssca.createintermediate()
    cc = ssca.certchain()
    (cert,key) = ssca.hostcert('testhost.domain.org')
    (cert,key) = ssca.usercert('TestUserOne')
    
    
    