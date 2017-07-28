#!/usr/bin/env python

import logging
import os
import StringIO

from ConfigParser import ConfigParser, SafeConfigParser
from ConfigParser import NoOptionError

from autopyfactory.apfexceptions import ConfigFailure
from autopyfactory.configloader import Config, ConfigManager
from autopyfactory.interfaces import ConfigInterface

from vc3client.client import VC3ClientAPI
from vc3infoservice.infoclient import  InfoMissingPairingException, InfoConnectionFailure


class VC3(ConfigInterface):
    def __init__(self, factory, config, section):

        self.log = logging.getLogger("autopyfactory.configplugin")
        self.factory = factory
        self.fcl = factory.fcl
        self.requestname = config.generic_get(section, 
                                              'config.auth.vc3.requestname', 
                                              default_value='all')

        self.vc3clientconf = config.generic_get(section, 
                                                'config.auth.vc3.vc3clientconf', 
                                                default_value=os.path.expanduser('~/.vc3/vc3-client.conf'))

        self.log.info("Config is %s" % ns.configpath)
        self.tempfile = config.generic_get(section, 
                                                'config.auth.vc3.tempfile', 
                                                default_value=os.path.expanduser('~/auth.conf.tmp'))
        cp = ConfigParser()
        cp.read(self.vc3clientconf)
        self.vc3api = VC3ClientAPI(cp)
        self.log.info('ConfigPlugin: Object initialized.')
    
    def getConfig(self):
        cp = Config()
        self.log.debug("Generating config object...")
        s = "# auth.conf from VC3 auth config plugin \n"
        if self.requestname == 'all':
            rlist = self.vc3api.listRequests()
            for r in rlist:
                if r.authconf is not None:
                    b64authconf = r.authconf
                    authconf = self.vc3api.decode(b64authconf)
                    s += "%s \n" % authconf
                    s += " \n"
            self.log.debug("Aggregated auth.conf entries from all Requests.")
            self.log.debug("Contents: %s" % s)
        else:
            r = self.vc3api.getRequest(self.requestname)
            b64authconf = r.authconf
            authconf = self.vc3api.decode(b64authconf)
            s += "%s \n" % authconf
            s += " \n"
        s = _raw_string(s)
        sio = StringIO.StringIO(s)
        self.log.debug("Config file string created. Reading into Config parser")
        cp.readfp(sio)
        self.log.debug("Done.")
        tf = open( self.tempfile, 'w')
        cp.write(tf)
        tf.close()
        self.log.debug("Wrote contents of config to %s" % self.tempfile)
        return cp
        
        
    def _raw_string(s):
        '''
        Converts from regular string (with escaped codes) to Python raw string. 
        '''
        if isinstance(s, str):
            s = s.encode('string-escape')
        elif isinstance(s, unicode):
            s = s.encode('unicode-escape')
        return s    
        