#!/usr/bin/env python

import logging
import os
import time
import errno
import StringIO
import traceback

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
                                                default_value=os.path.expanduser('~/queues.conf.tmp'))

        # number of seconds before we start to cleanup a queue that disappared
        # from the infoservice
        self.timeghostqueue = config.generic_get(section, 
                'config.queues.vc3.timeghostqueue', 
                default_value=60 * 15)         # fifteen minutes, in seconds

        # make sure we do not inheret queues from a previous run.
        if os.path.exists(self.tempfile):
            os.remove(self.tempfile)

        cp = ConfigParser()
        cp.read(self.vc3clientconf)
        self.vc3api = VC3ClientAPI(cp)
        self.log.info('VC3 Queues Config plugin: Object initialized.')
    
    def getConfig(self):
        self.log.debug("Generating queues config object...")
        cp = ConfigParser()

        self.log.debug("Reading defaults file for queues.conf")
        if os.path.exists(self.defaults):
            cp.read(self.defaults)

        rlist = self.get_requests()

        if rlist is None:
            self.log.warning("Could not read requests from infoservice. queues.conf will not be updated.")
            if os.path.exists(self.tempfile):
                self.log.debug("Reading previous queues definitions.")
                cp.read(self.tempfile)
        else:
            for r in rlist:
                if r.state != 'new' and r.state != 'validated' and r.state != 'terminated':
                    self.append_conf_of_request(cp, r)

            self.log.debug("Aggregated queues.conf entries from all Requests. Config has %s sections" % len(cp.sections()))

            tf = open( self.tempfile, 'w')
            tf.write("# queues.conf from VC3 auth config plugin \n")
            cp.write(tf)
            tf.close()
            self.log.debug("Wrote contents of config to %s" % self.tempfile)

        return cp

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

    def append_conf_of_request(self, config, request):
        if request.queuesconf is not None:

            previous_sections = set(config.sections())
            raw = self.vc3api.decode(request.queuesconf)
            self.append_conf_from_str(config, raw)

            new_sections = set(config.sections()) - previous_sections

            for section in new_sections:
                try:
                    self.add_transfer_files(config, section, request)
                    self.check_section(cp, section)
                except Exception, e:
                    self.log.warning("Error when adding request '%s' to queues.conf. Ignoring queue.", request.name)
                    self.log.debug(traceback.format_exc(None))
                    config.remove_section(section)

    def append_conf_from_str(self, config, string):
        buf = StringIO.StringIO(string)
        config.readfp(buf)

    def check_section(self, config, section):
        # turn config into a dict, so that values are interpolated. An invalid
        # value should generate an exception:
        d = dict(config.items(section))


    def add_transfer_files(self, config, section, request):

        env_names = []
        transfer_files = []

        if config.has_option(section, 'vc3.environments'):
            env_names = config.get(section, 'vc3.environments').split(',')

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

        for env_name in env_names:
            self.log.debug("Retrieving environment: %s" % env_name)
            try:
                environment = self.vc3api.getEnvironment(env_name)
            except Exception, e:
                self.log.debug("Failed to retrieve environment %s" % env_name)
                raise

            if environment.files:
                for fname in environment.files:
                    localname = os.path.join(localdir, fname)
                    with open(localname, 'w') as f:
                        f.write(self.vc3api.decode(environment.files[fname]))
                        transfer_files.append(localname)

        if request.headnode:
            try:
                self.log.debug("Writing condor pool password stage-out file for '%s'" % request.name)

                headnode = self.vc3api.getNodeset(request.headnode)
                localname = os.path.join(localdir, config.get(section, 'condor_password_filename'))
                with open(localname, 'w') as f:
                    f.write(self.vc3api.decode(config.get(section, 'condor_password')))
                    transfer_files.append(localname)
            except Exception, e:
                self.log.debug("Failed to retrieve headnode password information for %s" % request.name)

        plugin = config.get(section, 'batchsubmitplugin', None)
        if plugin is None:
            self.log.debug("section %s has no batchsubmitplugin defined." % plugin)
            return

        plugin = plugin.lower()
        config.set(section, 'batchsubmit.' + plugin + '.condor_attributes.transfer_input_files', ','.join(transfer_files))

