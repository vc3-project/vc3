#!/usr/bin/env python 
__author__ = "John Hover, Jose Caballero"
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
import subprocess
import sys
import time

from ConfigParser import ConfigParser
     

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
    
    Files placed in <vardir>/ssh/<name>/<principal>/
    
    ssh-keygen -t rsa -b 4096 -C "user.resource" -P "" -f "./user.resource.key" -q
    
    '''    
    def __init__(self, config, name='sshstore'):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)
        self.name = name
        self.vardir = os.path.expanduser(config.get('credible', 'vardir') )
        #self.vardir = os.path.expanduser(config.get('credible', 'vardir') )
        self.sshdir = "%s/ssh/%s" % (self.vardir, self.name)
        try:
            os.makedirs(self.sshdir) 
        except Exception, e:
            self.log.debug("problem making sshdir: %s %s" % (self.sshdir, e) )
            
        self.bitlength = config.get('credible-ssh','bitlength')
        self.keytype = config.get('credible-ssh','keytype')
        self.log.debug("sshdir is %s " % self.sshdir)
        
        
    def getkeys(self, principal = 'testuser.testresource'):
        self.log.debug("Getting keys for principal %s" % principal)    
        filepath = "%s/%s/%s" % (self.sshdir, principal, principal)
        if not os.path.isfile(filepath):
            self._genkeys(principal)
        
        pubkey = open("%s.pub" % filepath).read()
        privkey = open("%s" % filepath).read()
        return (pubkey, privkey)  
        
    def _genkeys(self, principal = 'testuser.testresource'):
        self.log.debug("genkeys for %s " % principal)
        filepath = "%s/%s/%s" % (self.sshdir, principal, principal) 
        filedir = "%s/%s" % (self.sshdir, principal)
        self.log.debug("filedir is %s" % filedir)
        try:
            os.makedirs(filedir)
        except:
            pass

        cmd =  "ssh-keygen "
        cmd += "-t %s " % self.keytype
        cmd += "-b %s " % self.bitlength
        cmd += '-C "%s" ' % principal
        cmd += '-P "" '
        cmd += '-f "%s" ' %  filepath
        self.log.debug("Command is %s" % cmd )
        o = _runtimedcommand(cmd)
        

class SSCA(object):
    '''
    Represents a Self-Signed Certificate authority. 
    '''
    def __init__(self, config, name='defaultca'):
        self.log = logging.getLogger()
        #self.log.setLevel(logging.DEBUG)
        self.caname = name
        self.vardir = os.path.expanduser(config.get('credible', 'vardir') )
        self.cadir = "%s/ssca/%s" % (self.vardir, self.caname)
        self.roottemplate=os.path.expanduser(config.get('credible-ssca', 'roottemplate'))
        self.intermediatetemplate=os.path.expanduser(config.get('credible-ssca', 'intermediatetemplate'))
        self.country = config.get('credible-ssca', 'country')   
        self.state = config.get('credible-ssca', 'state')  
        self.locality = config.get('credible-ssca', 'locality')
        self.organization = config.get('credible-ssca', 'organization')
        self.orgunit = config.get('credible-ssca', 'orgunit')
        self.email = config.get('credible-ssca', 'email')
        self.bitlength = config.get('credible-ssca' , 'bitlength')
        self.log.info("[SSCA:%s] initted" % self.caname)
        self.log.info("[SSCA:%s] vardir is %s" %  (self.caname, self.vardir))
        self._createroot()
        self._createintermediate()
       
    def _createroot(self):
        # Handle root CA
        self.log.info("Checking/making root CA")
       
        if not os.path.isfile("%s/root/private/root.key.pem" % self.cadir):
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
            #fd = {               
            #      }
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
            ccf = open(ccfile, 'w')
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
        '''  
        self.log.debug("Generating new private key for host %s" % hostname)
        cmd =  "openssl genrsa -aes256 "
        cmd += " -passout pass:abcdef " 
        cmd += "-out %s/intermediate/private/%s.key.pem %s " % ( self.cadir,
                                                                 hostname,
                                                                 self.bitlength)
        o = _runtimedcommand(cmd)
        os.chmod("%s/intermediate/private/%s.key.pem" % (self.cadir, hostname) , 400)
        
        # Remove passphrase
        cmd =  "openssl rsa "
        cmd += " -passin pass:abcdef "
        cmd += "-in %s/intermediate/private/%s.key.pem " % ( self.cadir,
                                                            hostname) 
        cmd += "-out %s/intermediate/private/%s.keynopw.pem " % ( self.cadir,
                                                                     hostname)
        o = _runtimedcommand(cmd)
        os.chmod("%s/intermediate/private/%s.keynopw.pem" % (self.cadir, hostname) , 400)
    
        self.log.debug("Creating CSR for host cert using new private key...")
        cmd =  "openssl req -config %s/intermediate/openssl.cnf " % self.cadir
        cmd += "-key %s/intermediate/private/%s.keynopw.pem " % (self.cadir, hostname)
        cmd += "-new -sha256 -out %s/intermediate/csr/%s.csr.pem " % (self.cadir, hostname)
        cmd += '-subj "/C=%s/ST=%s/O=%s/OU=%s/CN=%s/emailAddress=%s"' % ( self.country,
                                                                                       self.state,
                                                                                       self.organization,
                                                                                       self.orgunit,
                                                                                       hostname,
                                                                                       self.email)
        self.log.debug("Command is %s" % cmd)
        o = _runtimedcommand(cmd)
        
        self.log.debug("Signing CSR with intermediate private key...")
        cmd =  "openssl ca -batch -config %s/intermediate/openssl.cnf " % self.cadir
        cmd += "-extensions server_cert -days 375 -notext -md sha256 "
        cmd += "-in %s/intermediate/csr/%s.csr.pem " % (self.cadir, hostname) 
        cmd += "-out %s/intermediate/certs/%s.cert.pem " % (self.cadir, hostname)
        self.log.debug("Command is %s" % cmd)
        o = _runtimedcommand(cmd)
        #os.chmod("%s/intermediate/certs/%s.cert.pem " % (self.cadir, hostname), 444)
        
        self.log.debug("Verifying new host certificate...")
        cmd = "openssl x509 -noout -text -in %s/intermediate/certs/%s.cert.pem " % (self.cadir, hostname)
        o = _runtimedcommand(cmd)
        self.log.debug("Output is %s " % o)
        
        
    def gethostcert(self, hostname):
        self.log.info("Making/retrieving host cert for %s" % hostname)
        hcf = "%s/intermediate/certs/%s.cert.pem" % (self.cadir, hostname)
        hkf = "%s/intermediate/private/%s.keynopw.pem" % (self.cadir, hostname)
        if not os.path.isfile(hcf):
            self._makehostcert(hostname)
        else:
            self.log.debug("Host cert %s exists. Returning..." % hostname) 
        hcfh = open(hcf, 'r')
        hkfh = open(hkf, 'r')
        c = hcfh.read()
        k = hkfh.read()
        hcfh.close()
        hkfh.close()
        return (c,k)

    def getusercert(self, subject):
        self.log.info("Making/retrieving user cert for %s" % subject)
        ucf = "%s/intermediate/certs/%s.cert.pem" % (self.cadir, subject)
        ukf = "%s/intermediate/private/%s.keynopw.pem" % (self.cadir, subject)
        if not os.path.isfile(ucf):
            self._makeusercert(subject)
        else:
            self.log.debug("User cert %s exists. Returning..." % subject) 
        ucfh = open(ucf, 'r')
        ukfh = open(ukf, 'r')
        c = ucfh.read()
        k = ukfh.read()
        ucfh.close()
        ukfh.close()
        return (c,k)
    
    def _makeusercert(self, subject):
        '''
        '''  
        self.log.debug("Generating new private key for user %s" % subject)
        cmd =  "openssl genrsa -aes256 "
        cmd += " -passout pass:abcdef " 
        cmd += "-out %s/intermediate/private/%s.key.pem %s " % ( self.cadir,
                                                                 subject,
                                                                 self.bitlength)
        o = _runtimedcommand(cmd)
        os.chmod("%s/intermediate/private/%s.key.pem" % (self.cadir, subject) , 400)
        
        # Remove passphrase
        cmd =  "openssl rsa "
        cmd += " -passin pass:abcdef "
        cmd += "-in %s/intermediate/private/%s.key.pem " % ( self.cadir,
                                                            subject) 
        cmd += "-out %s/intermediate/private/%s.keynopw.pem " % ( self.cadir,
                                                                     subject)
        o = _runtimedcommand(cmd)
        os.chmod("%s/intermediate/private/%s.keynopw.pem" % (self.cadir, subject) , 400)
    
        self.log.debug("Creating CSR for user cert using new private key...")
        cmd =  "openssl req -config %s/intermediate/openssl.cnf " % self.cadir
        cmd += "-key %s/intermediate/private/%s.keynopw.pem " % (self.cadir, subject)
        cmd += "-new -sha256 -out %s/intermediate/csr/%s.csr.pem " % (self.cadir, subject)
        cmd += '-subj "/C=%s/ST=%s/O=%s/OU=%s/CN=%s/emailAddress=%s"' % ( self.country,
                                                                                       self.state,
                                                                                       self.organization,
                                                                                       self.orgunit,
                                                                                       subject,
                                                                                       self.email)
        self.log.debug("Command is %s" % cmd)
        o = _runtimedcommand(cmd)
        
        self.log.debug("Signing CSR with intermediate private key...")
        cmd =  "openssl ca -batch -config %s/intermediate/openssl.cnf " % self.cadir
        cmd += "-extensions usr_cert -days 375 -notext -md sha256 "
        cmd += "-in %s/intermediate/csr/%s.csr.pem " % (self.cadir, subject) 
        cmd += "-out %s/intermediate/certs/%s.cert.pem " % (self.cadir, subject)
        self.log.debug("Command is %s" % cmd)
        o = _runtimedcommand(cmd)
        #os.chmod("%s/intermediate/certs/%s.cert.pem " % (self.cadir, subject), 444)
        
        self.log.debug("Verifying new user certificate...")
        cmd = "openssl x509 -noout -text -in %s/intermediate/certs/%s.cert.pem " % (self.cadir, subject)
        o = _runtimedcommand(cmd)
        self.log.debug("Output is %s " % o)
        
def test():
    cf = os.path.expanduser("~/etc/credible.conf")
    cp = ConfigParser()
    cp.read(cf)
    cp.set("credible-ssca","roottemplate", "etc/openssl.cnf.root.template")
    cp.set("credible-ssca","intermediatetemplate", "etc/openssl.cnf.intermediate.template")
    ssca = SSCA('catest', cp)
    cc = ssca.getcertchain()
    print("certchain is %s" % cc )
    (cert,key) = ssca.gethostcert('testhost.domain.org')
    print("hostcert is %s" % cert)
    print("hostkey is %s" % key)
    (cert,key) = ssca.getusercert('TestUserOne')
    print("usercert is %s" % cert)
    print("userkey is %s" % key)    

    # Test ssh key generation
    sska = SSHKeyManager('sshtest', cp)
    (pub,priv) = sska.getkeys("testuser")
    print("Pubkey is %s" % pub)
    print("privkey is %s" % priv)


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

    