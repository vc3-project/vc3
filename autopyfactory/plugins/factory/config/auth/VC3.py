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

        self.defaults = config.generic_get(section, 'config.auth.vc3.defaultsfile',
                                              default_value='/etc/autopyfactory/vc3authdefaults.conf')

        self.log.info("Config is %s" % self.vc3clientconf)
        self.tempfile = config.generic_get(section, 
                                                'config.auth.vc3.tempfile', 
                                                default_value=os.path.expanduser('~/auth.conf.tmp'))
        cp = ConfigParser()
        cp.read(self.vc3clientconf)
        self.vc3api = VC3ClientAPI(cp)
        self.log.info('VC3 Auth Config plugin: Object initialized.')
    
    def getConfig(self):
        self.log.debug("Generating auth config object...")
        cp = ConfigParser()

        self.log.debug("Reading defaults file for auth.conf")
        if os.path.exists(self.defaults):
            cp.read(self.defaults)

        # we read the last version so that no queue is orphaned in case the
        # infoservice is not available
        if os.path.exists(self.tempfile):
            self.log.debug("Reading previous auth definitions.")
            cp.read(self.defaults)

        rlist = self.get_requests()
        if rlist is None:
            self.log.warning("Could not read requests from infoservice. Using previous definitions.")
            return cp

        for r in rlist:
            self.append_conf_of_request(cp, r)

        self.log.debug("Aggregated auth.conf entries from all Requests.")
        self.log.debug("Done. Auth has %s sections" % len(cp.sections()))

        tf = open( self.tempfile, 'w')
        tf.write("# auth.conf from VC3 auth config plugin \n")
        cp.write(tf)
        tf.close()
        self.log.debug("Wrote contents of config to %s" % self.tempfile)

        return cp

    def append_conf_of_request(self, config, request):
        if request.authconf is not None:
            raw = self.vc3api.decode(request.authconf)
            buf = StringIO.StringIO(raw)
            config.readfp(buf)

    def get_requests(self):
        rlist = None
        try:
            if self.requestname == 'all':
                rlist = self.vc3api.listRequests()
            else:
                rlist = [ self.vc3api.getRequest(self.requestname) ]

            if len(rlist) < 1:
                self.log.debug("Could not find requests at the infoservice.")

        except InfoConnectionFailure as e:
            # On connection error, we return None
            pass
        return rlist
 
        
