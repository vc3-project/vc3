#!/usr/bin/env python

import logging
import os
import errno
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
        self.log.debug("Reading defaults file for queues.conf")
        df = open(self.defaults, 'r')
        dstr = df.read()
        df.close()

        cp = Config()
        self.append_conf_from_str(cp, dstr)

        if self.requestname == 'all':
            rlist = self.vc3api.listRequests()
            for r in rlist:
                self.append_conf_of_request(cp, r)
            self.log.debug("Aggregated queues.conf entries from all Requests.")
        else:
            r = self.vc3api.getRequest(self.requestname)
            self.append_conf_of_request(cp, r)

        self.log.debug("Done. Config has %s sections" % len(cp.sections()))

        tf = open( self.tempfile, 'w')
        tf.write("# queues.conf from VC3 auth config plugin \n")
        cp.write(tf)
        tf.close()
        self.log.debug("Wrote contents of config to %s" % self.tempfile)

        return cp

    def append_conf_of_request(self, config, request):
        if request.queuesconf is not None:
            raw = self.vc3api.decode(request.queuesconf)
            cpr = Config()
            self.append_conf_from_str(cpr, raw) # so we know the new section names
            self.append_conf_from_str(config, raw)

            for section in cpr.sections():
                self.add_transfer_files(config, section, request) # wrong, should come from nodesets

    def append_conf_from_str(self, config, string):
        buf = StringIO.StringIO(string)
        config.readfp(buf)

    def add_transfer_files(self, config, section, request):
        env_name = config.get(section, 'vc3.environment', None)

        if env_name is None:
            return

        self.log.debug("Retrieving environment: %s" % env_name)
        environment = self.vc3api.getEnvironment(env_name)
        if environment is None:
            self.log.debug("Failed to retrieve environment %s" % env_name)
            return

        # create scratch local directory to stage input files.
        # BUG: NEED TO CLEANUP THESE FILES WHEN REQUEST IS FINISHED 
        localdir = os.path.join(os.path.expanduser('~/var/vc3/stage-out'), request.name)

        try:
            os.makedirs(localdir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        transfer_files = []
        if environment.files:
            for fname in environment.files:
                localname = os.path.join(localdir, fname)
                with open(localname, 'w') as f:
                    f.write(self.vc3api.decode(environment.files[fname]))
                    transfer_files.append(localname)

        if len(transfer_files) < 1:
            return

        plugin = config.get(section, 'batchsubmitplugin', None)
        if plugin is None:
            self.log.debug("section %s has no batchsubmitplugin defined." % plugin)
            return

        plugin = plugin.lower()

        config.set(section, 'batchsubmit.' + plugin + '.condor_attributes', 'should_transfer_files=YES,transfer_input_files =' + '\\,'.join(transfer_files))

