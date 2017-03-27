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
    
    Files placed in vardir/ssh/<name>/<principal>/
    
    ssh-keygen -t rsa -b 4096 -C "user.resource" -P "" -f "./user.resource.key" -q
    
    '''    
    def __init__(self, name, config):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.name = name
        self.vardir = os.path.expanduser(config.get('credible', 'vardir') )
        self.sshdir = "%s/ssh/%s" % (self.vardir, self.name)
        self.bitlength = config.get('credible-ssh','bitlength')
        self.keytype = config.get('credible-ssh','keytype')
        
    def getkeys(self, principal = 'testuser.testresource'):
        self.log.debug("Getting keys for principal %s" % principal)    

        pubkey = "AAAAA"
        privkey = 'BBBBBB'
        return (pubkey, privkey)

    
    def _loadkeys(self):
        self.log.debug("Loading existing keys...")
    
        
    def _genkeys(self, principal = 'testuser.testresource'):
        
        filepath = "%s/%s/%s" % (self.sshdir, principal, principal) 
        cmd =  "ssh-keygen "
        cmd += "-t %s " % self.keytype
        cmd += "-b %s" % self.bitlength
        cmd += '-C "%s" ' % principal
        cmd += '-P "" '
        cmd += '-f "%s" ' %  filepath
        



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
        self._createroot()
        self._createintermediate()
       
   

    def _createroot(self):
        # Handle root CA
        self.log.info("Checking/making root CA")
       
        if not os.path.isfile("%s/root/private/ca.key.pem" % self.cadir):
            self.log.info("Making directories...")
            for leaf in ["root/private", "root/certs", "root/newcerts", "root/crl", "root/csr"]:
                try:
                    ld = "%s/%s" % (self.cadir, leaf)
                    self.log.debug("[SSCA:%s] Making/confirming root CA dir %s" % (self.caname, ld))
                    os.makedirs(ld)
                except:
                    pass 
            self.log.info("Making root CA key...")
            cmd =  "openssl genrsa -aes256 -passout pass:abcdef "
            cmd += "-out %s/root/private/root.key.pem 4096 " % self.cadir 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)
            cmd =  "openssl rsa -passin pass:abcdef "
            cmd += "-in %s/root/private/root.key.pem " % self.cadir
            cmd += "-out %s/root/private/root.keynopw.pem " % self.cadir 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)                                                                                                                
            os.chmod("%s/root/private/root.keynopw.pem" % self.cadir, 400)
            os.chmod("%s/root/private/root.key.pem" % self.cadir,  400)
            self.log.info("Making index, serial, crlnumber files...")
            open("%s/root/index.txt" % self.cadir,'a').close()
            for fn in ['serial','crlnumber']:
                fi = open("%s/root/%s" % ( self.cadir, fn) ,'w')
                fi.write("1000\n")
                fi.close()
            self.log.info("Creating openssl.cnf")
            oct = open(self.roottemplate, 'r')
            tt = oct.read()
            #self.log.debug("template= %s" % tt)
            fd = {               
                  }
            out = tt.format(vardir = self.vardir ,
                            sscaname = self.caname,
                            country = self.country,
                            state = self.state,
                            locality = self.locality,
                            organization = self.organization,
                            orgunit = self.orgunit,
                            email = self.email    )
            oc = open("%s/root/openssl.cnf" % self.cadir, 'w')
            oc.write(out)
            oc.close()
                   
            self.log.info("Making root CA request and cert...")
            cmd =  "openssl req -config %s/root/openssl.cnf " % self.cadir  
            cmd += "-key %s/root/private/root.keynopw.pem " % self.cadir 
            cmd += "-new -x509 -days 7300 -sha256 -extensions v3_ca " 
            cmd += "-out %s/root/certs/root.cert.pem "  % self.cadir 
            cmd += '-subj "/C=%s/ST=%s/O=%s/OU=%s/CN=%s-Root/emailAddress=%s"' % ( self.country,
                                                                                       self.state,
                                                                                       self.organization,
                                                                                       self.orgunit,
                                                                                       self.caname,
                                                                                       self.email
                                                                                      )
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)                                                                     
            os.chmod("%s/root/certs/root.cert.pem" % self.cadir,  444)
            self.log.info("Emitting CA certificate...")
            #openssl x509 -noout -text -in root/certs/ca.cert.pem
        else:
            self.log.info("Root CA already created.")
        self.log.info("Done.")

    def _createintermediate(self):
        # Handle intermediate CA
        self.log.info("Checking/making intermediate CA")        
        if not os.path.isfile("%s/intermediate/private/intermediate.key.pem" % self.cadir):
            self.log.info("Making directories...")
            for leaf in ["intermediate/private", "intermediate/certs", "intermediate/newcerts", "intermediate/crl", "intermediate/csr"]:
                try:
                    ld = "%s/%s" % (self.cadir, leaf)
                    self.log.debug("[SSCA:%s] Making/confirming intermediate CA dir %s" % (self.caname, ld))
                    os.makedirs(ld)
                except:
                    pass        
            self.log.info("Making index, serial, crlnumber files...")
            open("%s/intermediate/index.txt" % self.cadir,'a').close()
            for fn in ['serial','crlnumber']:
                fi = open("%s/intermediate/%s" % ( self.cadir, fn) ,'w')
                fi.write("1000\n")
                fi.close()
                
            self.log.info("Making intermediate CA key...")
            cmd =  "openssl genrsa "
            cmd += "-aes256 "
            cmd += "-passout pass:abcdef "
            cmd += " -out %s/intermediate/private/intermediate.key.pem 4096" % self.cadir 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)
            
            cmd =  "openssl rsa -passin pass:abcdef " 
            cmd += "-in %s/intermediate/private/intermediate.key.pem " % self.cadir
            cmd += " -out %s/intermediate/private/intermediate.keynopw.pem" % self.cadir 
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)
            
            os.chmod("%s/intermediate/private/intermediate.keynopw.pem" % self.cadir, 400)
            os.chmod("%s/intermediate/private/intermediate.key.pem" % self.cadir,  400)
            

            self.log.info("Creating openssl.cnf")
            oct = open(self.intermediatetemplate, 'r')
            tt = oct.read()
            #self.log.debug("template= %s" % tt)
            fd = {               
                  }
            out = tt.format(vardir = self.vardir ,
                            sscaname = self.caname,
                            country = self.country,
                            state = self.state,
                            locality = self.locality,
                            organization = self.organization,
                            orgunit = self.orgunit,
                            email = self.email    )
            oc = open("%s/intermediate/openssl.cnf" % self.cadir, 'w')
            oc.write(out)
            oc.close()
                   
            self.log.info("Making intermediate request")
            cmd =  "openssl req -config %s/intermediate/openssl.cnf " % self.cadir  
            cmd += "-new -sha256 " 
            cmd += "-key %s/intermediate/private/intermediate.keynopw.pem " % self.cadir 
            cmd += "-out %s/intermediate/csr/intermediate.csr.pem "  % self.cadir 
            cmd += '-subj "/C=%s/ST=%s/O=%s/OU=%s/CN=%s-Intermediate/emailAddress=%s"' % ( self.country,
                                                                                       self.state,
                                                                                       self.organization,
                                                                                       self.orgunit,
                                                                                       self.caname,
                                                                                       self.email
                                                                                      )
            self.log.debug("Command is %s" % cmd)
            o = _runtimedcommand(cmd)
            #os.chmod("%s/intermediate/certs/ca.cert.pem" % self.cadir,  444)
            
            self.log.info("Signing intermediate request, generating intermediate...")
            cmd =  "openssl ca -batch -config %s/root/openssl.cnf "  % self.cadir
            cmd += "-extensions v3_intermediate_ca -days 3650 -notext -md sha256 "
            cmd += "-in %s/intermediate/csr/intermediate.csr.pem "  % self.cadir
            cmd += "-out %s/intermediate/certs/intermediate.cert.pem "  % self.cadir
            o = _runtimedcommand(cmd)
            # chmod 444 intermediate/certs/intermediate.cert.pem         
             
                                                                     
            #self.log.info("Emitting CA certificate...")
            #openssl x509 -noout -text -in intermediate/certs/ca.cert.pem
        else:
            self.log.info("Intermediate CA already created.")
        self.log.info("Done.")
    
    def _makecertchain(self):
        self.log.info("Create cert chain file...")
        ccfile = "%s/intermediate/certs/ca-chain.cert.pem" % self.cadir
        if not os.path.isfile(ccfile):
            rcaf = open("%s/root/certs/root.cert.pem" % self.cadir)
            icaf = open("%s/intermediate/certs/intermediate.cert.pem" % self.cadir)
            rcastr = rcaf.read()
            rcaf.close()
            icastr = icaf.read()
            icaf.close()
            ccf = open(ccfile)
            ccf.write(rcastr)
            ccf.write(icastr)
            ccf.close()
            os.chmod("%s/intermediate/certs/ca-chain.cert.pem" % self.cadir, 444)
        else:
            self.log.debug("Cert chain file already exists.")
    
    def getcertchain(self):
        self.log.info("Check/create/return cert chain file...")
        ccfile = "%s/intermediate/certs/ca-chain.cert.pem" % self.cadir
        self.log.debug("Certchain file is %s" % ccfile)
        if not os.path.isfile(ccfile):
            self._makecertchain()
        else:
            self.log.debug("Certchain exists. Returning.")
        cf = open(ccfile, 'r')
        ccfstring = cf.read()
        cf.close()
        return ccfstring
    
    def _makehostcert(self, hostname):
        '''
     echo "Generating new private key for host cert..."
 openssl genrsa -aes256 -passout pass:abcdef\
    -out intermediate/private/$hostname.key.pem 2048
 chmod 400 intermediate/private/$hostname.key.pem
 openssl rsa -passin pass:abcdef -in intermediate/private/$hostname.key.pem \
  -out intermediate/private/$hostname.keynopw.pem
 chmod 400 intermediate/private/$hostname.keynopw.pem

 echo "Creating CSR for host cert using new private key..."
 openssl req -config intermediate/openssl.cnf \
    -key intermediate/private/$hostname.keynopw.pem \
    -new -sha256 -out intermediate/csr/$hostname.csr.pem \
    -subj "/C=US/ST=NY/O=BNL/OU=SDCC/CN=$hostname/emailAddress=jhover@bnl.gov"

 echo "Signing CSR with intermediate private key..."
openssl ca -batch -config intermediate/openssl.cnf \
      -extensions server_cert -days 375 -notext -md sha256 \
      -in intermediate/csr/$hostname.csr.pem \
      -out intermediate/certs/$hostname.cert.pem
 chmod 444 intermediate/certs/$hostname.cert.pem

 echo "Verifying new host certificate..."
 openssl x509 -noout -text \
    -in intermediate/certs/$hostname.cert.pem


    '''
      
        
        
        self.log.debug("Making cert for %s" % hostname)
    
    
    
    
        
    def gethostcert(self, hostname):
        self.log.info("Making/retrieving host cert for %s" % hostname)
        hcf = "%s/intermdiate/certs/%s.cert.pem" % (self.cadir, hostname)
        hkf = "%s/intermediate/private/%s.cer.keynopw" % (self.cadir, hostname)
        if not os.path.isfile(hcf):
            _makehostcert(hostname)
        else:
            self.log.debug("Host cert %s exists. Returning." % hostname) 
        hcfh = open(hcf, 'r')
        hkfh = open(hkf, 'r')
        c = hcfh.read()
        k = hkfh.read()
        hcfh.close()
        hkfh.close()
        return (c,k)

    def getusercert(self, hostname):
        ucf = ""
        c = "UUUUUUU"
        k = "PPPPPPP"
        return (c,k)
    
    

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    cf = os.path.expanduser("etc/credible.conf")
    cp = ConfigParser()
    cp.read(cf)
    cp.set("credible-ssca","roottemplate", "etc/openssl.cnf.root.template")
    cp.set("credible-ssca","intermediatetemplate", "etc/openssl.cnf.intermediate.template")
    ssca = SSCA('catest', cp)
    ssca._createroot()
    ssca._createintermediate()
    cc = ssca.getcertchain()
    print("certchain is %s" % cc )
    (cert,key) = ssca.gethostcert('testhost.domain.org')
    (cert,key) = ssca.getusercert('TestUserOne')
    
    
    