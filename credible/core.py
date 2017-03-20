#!/usr/bin/env python 

__author__ = "John Hover, Jose Caballero"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

from optparse import OptionParser
from ConfigParser import ConfigParser
from pluginmanager.plugin import PluginManager

class SSHKeyManager(object):
    '''
    Handles generation, storage, and retrieval of SSH keypairs. 
    
    '''    
    def __init__(self, name, config):
        self.name = name


class SSCA(object, config):
    '''
    Represents a Self-Signed Certificate authority. 
    '''
    
    def __init__(self, caname):
        self.caname = caname

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
    ssca = SSCA('catest')
    ssca.createroot()
    ssca.createintermediate()
    cc = ssca.certchain()
    (cert,key) = ssca.hostcert('testhost.domain.org')
    (cert,key) = ssca.usercert('TestUserOne')
    
    
    