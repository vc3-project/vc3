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
                                              'config.queues.vc3.requestname', 
                                              default_value='all')
        self.defaults = config.generic_get(section, 'config.queues.vc3.defaultsfile',
                                              default_value='/etc/autopyfactory/vc3defaults.conf')

        self.vc3clientconf = config.generic_get(section, 
                                                'config.queues.vc3.vc3clientconf', 
                                                default_value=os.path.expanduser('~/.vc3/vc3-client.conf'))

        self.log.info("Config is %s" % self.vc3clientconf )
        self.tempfile = config.generic_get(section, 
                                                'config.queues.vc3.tempfile', 
                                                default_value=os.path.expanduser('~/auth.conf.tmp'))
        cp = ConfigParser()
        cp.read(self.vc3clientconf)
        self.vc3api = VC3ClientAPI(cp)
        self.log.info('VC3 Queues Config plugin: Object initialized.')
    
    def getConfig(self):
        self.log.debug("Generating queues config object...")
        s = ""
        self.log.debug("Reading defaults file for queues.conf")
        df = open(self.defaults, 'w')
        dstr = df.read()
        df.close()
        s += dstr
        self.log.debug("Defaults read: %s" % s)
              
        if self.requestname == 'all':
            rlist = self.vc3api.listRequests()
            for r in rlist:
                if r.queuesconf is not None:
                    s += self.vc3api.decode(r.queuesconf)
            self.log.debug("Aggregated queues.conf entries from all Requests.")
        else:
            r = self.vc3api.getRequest(self.requestname)
            if r.queuesconf is not None:
                s += self.vc3api.decode(r.queuesconf)
        self.log.debug("Contents: %s" % s)            
        buf = StringIO.StringIO(s)
        self.log.debug("Buffer file created: %s. Reading into Config parser..." % s)
        cp = Config()
        cp.readfp(buf)
        self.log.debug("Done. Config has %s sections" % len(cp.sections()))
        tf = open( self.tempfile, 'w')
        tf.write("# queues.conf from VC3 auth config plugin \n")
        cp.write(tf)
        tf.close()
        self.log.debug("Wrote contents of config to %s" % self.tempfile)
        return cp
        

