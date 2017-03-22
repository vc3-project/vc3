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
import subprocess
import time


from optparse import OptionParser
from ConfigParser import ConfigParser
from pluginmanager.plugin import PluginManager

def _runtimedcommand(cmd):
    log = logging.getLogger()
    before = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = None
    (out, err) = p.communicate()
    delta = time.time() - before
    log.debug('%s seconds to perform command' %delta)
    if p.returncode == 0:
        log.debug('Leaving with OK return code.')
    else:
        log.warning('Leaving with bad return code. rc=%s err=%s out=%s' %(p.returncode, err, out ))
        out = None
    return out


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
        self.vardir = os.path.expanduser(config.get('credible', 'vardir') )
        self.cadir = "%s/ssca/%s" % (self.vardir, self.caname)
        self.roottemplate=config.get('credible-ssca', 'roottemplate')
        self.intermediatetemplate=config.get('credible-ssca', 'intermediatetemplate')
        self.country = config.get('credible-ssca', 'country')   
        self.state = config.get('credible-ssca', 'state')  
        self.locality = config.get('credible-ssca', 'locality')
        self.organization = config.get('credible-ssca', 'organization')
        self.orgunit = config.get('credible-ssca', 'orgunit')
        self.email = config.get('credible-ssca', 'email')
        self.log.info("[SSCA:%s] initted" % self.caname)
        self.log.info("[SSCA:%s] vardir is %s" %  (self.caname, self.vardir)) 

    def createroot(self):
        # Handle root CA
        self.log.info("Making root CA")
        self.log.info("Making directories...")
        for leaf in ["root/private", "root/certs", "root/newcerts", "root/crl", "root/csr"]:
            try:
                ld = "%s/%s" % (self.cadir, leaf)
                self.log.debug("[SSCA:%s] Making/confirming root CA dir %s" % (self.caname, ld))
                os.makedirs(ld)
            except:
                pass        
        if not os.path.isfile("%s/root/private/ca.key.pem" % self.cadir):
            self.log.info("Making root CA key...")
            cmd = "openssl genrsa -aes256 -passout pass:abcdef -out %s/root/private/ca.key.pem 4096" % self.cadir 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)
            cmd = "openssl rsa -passin pass:abcdef  -in %s/root/private/ca.key.pem  -out %s/root/private/ca.keynopw.pem" % (self.cadir,
                                                                                                                            self.cadir) 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)                                                                                                                
            os.chmod("%s/root/private/ca.keynopw.pem" % self.cadir, 400)
            os.chmod("%s/root/private/ca.key.pem" % self.cadir,  400)
            self.log.info("Making index, serial, crlnumber files...")
            open("%s/root/index.txt" % self.cadir,'a').close()
            for fn in ['serial','crlnumber']:
                fi = open("%s/root/%s" % ( self.cadir, fn) ,'w')
                fi.write("1000\n")
                fi.close()
            self.log.info("Creating openssl.cnf")
            oct = open(self.roottemplate, 'r')
            tt = oct.read()
            self.log.debug("template= %s" % tt)
            #tt.format
            
            #oc = open("%s/root/openssl.cnf " % self.cadir. 'w')
            
            
            
                   
            self.log.info("Making root CA request and cert...")
            cmd =  "openssl req -config %s/root/openssl.cnf " % self.cadir  
            cmd += "-key %s/root/private/ca.keynopw.pem " % self.cadir 
            cmd += "-new -x509 -days 7300 -sha256 -extensions v3_ca " 
            cmd += "-out %s/root/certs/ca.cert.pem "  % self.cadir 
            cmd += '-subj "/C=%s/ST=%s/O=%s/OU=%s/CN=%s-Root/emailAddress=%s"' % ( self.country,
                                                                                       self.state,
                                                                                       self.organization,
                                                                                       self.orgunit,
                                                                                       self.caname,
                                                                                       self.email
                                                                                      )
            #chmod 444 root/certs/ca.cert.pem
            self.log.info("Emitting CA certificate...")
            #openssl x509 -noout -text -in root/certs/ca.cert.pem
        else:
            self.log.info("Root CA already created.")
        self.log.info("Done.")

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
    cp.set("credible-ssca","roottemplate", "etc/openssl.cnf.root.template")
    ssca = SSCA('catest', cp)
    ssca.createroot()
    ssca.createintermediate()
    cc = ssca.certchain()
    (cert,key) = ssca.hostcert('testhost.domain.org')
    (cert,key) = ssca.usercert('TestUserOne')
    
    
    