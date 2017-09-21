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

        # we read the last version so that no queue is orphaned in case the
        # infoservice is not available
        if os.path.exists(self.tempfile):
            self.log.debug("Reading previous queues definitions.")
            cp.read(self.defaults)

        previous_queues = cp.sections()

        rlist = self.get_requests()

        if rlist is None:
            self.log.warning("Could not read requests from infoservice. Using previous definitions.")
            return cp

        for r in rlist:
            self.append_conf_of_request(cp, r)

        self.log.debug("Aggregated queues.conf entries from all Requests.")
        self.clean_removed_queues(cp, previous_queues)
        self.log.debug("Done. Config has %s sections" % len(cp.sections()))

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


    def clean_removed_queues(self, config, previous_queues):
        now = time.time()

        found = {}
        for section in previous_queues:
            found[section] = False

        for section in config.sections():
            found[name] = True

        for section in [ section for section in found.keys() if not found[section] ]:
            if config.has_option(section, 'vc3.queue.lastupdate'):
                last = config.get(section, 'vc3.queue.lastupdate')
                if now - last > self.timeghostqueue:
                    self.log.debug('Old request %s. Setting running jobs to 0', section)
                    config.set(section, 'sched.keepnrunning.keep_running', 0)

    def append_conf_of_request(self, config, request):
        if request.queuesconf is not None:
            raw = self.vc3api.decode(request.queuesconf)
            cpr = Config()
            self.append_conf_from_str(cpr, raw) # so we know the new queue section names per nodeset
            self.append_conf_from_str(config, raw)

            for section in cpr.sections():
                config.set(section, 'vc3.queue.lastupdate', time.time())
                self.add_transfer_files(config, section, request) # wrong, should come from nodesets

    def append_conf_from_str(self, config, string):
        buf = StringIO.StringIO(string)
        config.readfp(buf)

    def add_transfer_files(self, config, section, request):

        if not config.has_option(section, 'vc3.environment'):
            return

        env_name = config.get(section, 'vc3.environment')

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

        plugin = config.get(section, 'batchsubmitplugin', None)
        if plugin is None:
            self.log.debug("section %s has no batchsubmitplugin defined." % plugin)
            return

        plugin = plugin.lower()

        config.set(section, 'batchsubmit.' + plugin + '.condor_attributes.transfer_input_files', ','.join(transfer_files))

