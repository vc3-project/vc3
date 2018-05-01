#!/bin/env python

'''VC3 Montoring plugin
 Copied over wholesale from autopyfactory-tools
 Provides methods for job, queue, and factory monitoring calls 
 Enters information into the configured infoservice. 

Info to publish: By Request, then broken down by factoryname (i.e. hostname?)

# Raw info for each allocation, by factory.
Request.statusraw =
       { "factoryid1" : {"nodeset1" : {  "<allocation1>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 },
                                         "<allocation2>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 }, 
                                      },
                         "nodeset2" : {  "<allocation1>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 },
                                         "<allocation3>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 }, 
                                      },
                        },
         "factoryid2" : {"nodeset1" : {  "<allocation4>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 },
                         "nodeset3" : {  "<allocation5>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 },
                                         "<allocation6>" : {'unsub' : 0, 'idle' : 10, 'running' : 5, 'removed' : 0, 'completed' : 0, 'held' : 0, 'error': 0 }, 
                                      },
                        },
        }

Note that the same nodeset can be in different factories,
and the same allocation can be in different nodesets.

# Aggregate numbers for this entire request.
# This is what Master lifecycle task would look at to determine overall
# (virtual) cluster state.
Request.status = { 'unsub' : 0,
                   'idle' : 10,
                   'running' : 5,
                   'removed' : 0,
                   'completed' : 0,
                   'held' : 0,
                   'error': 0
                  }

'''

import argparse   
import copy
import logging
import os
import subprocess
import time

from ConfigParser import SafeConfigParser

import htcondor

from vc3client.client import VC3ClientAPI
from vc3infoservice.infoclient import  InfoMissingPairingException, InfoConnectionFailure

from autopyfactory.interfaces import MonitorInterface
from autopyfactory.interfaces import _thread


class _vc3(_thread, MonitorInterface):
    
    def __init__(self, factory, config, section):
        _thread.__init__(self)

        self.log = logging.getLogger("autopyfactory.monitor")

        self.factory = factory
        self.apfqueuesmanager = self.factory.apfqueuesmanager
        self.apfqueues = self.apfqueuesmanager.queues

        self.factory.threadsregistry.add("plugin", self)
        interval = config.generic_get('Factory', 'monitor.vc3.interval', 'getint', default_value=30)
        self._thread_loop_interval = interval


        self.vc3clientconf = config.generic_get('Factory',
                                                'monitor.vc3.vc3clientconf',
                                                default_value=os.path.expanduser('~/.vc3/vc3-client.conf'))

        self.log.debug("VC3 client config is %s" % self.vc3clientconf )
        cp = SafeConfigParser()
        cp.readfp(open(self.vc3clientconf))

        self.vc3api = VC3ClientAPI(cp)

        self.log.info('Factory monitor: Object initialized.')


    def _run(self):

        self.log.debug('Starting')
        newinfo = self.getInfo()
        self.updateRequests(newinfo)
        self.log.debug('Leaving')


    def getInfo(self):
        '''
        get batch status info from each APFQueue
        output looks like this:

         info = {  "<queue1>" : { 'unsub' : 0,
                                  'idle' : 10,
                                  'running' : 5,
                                  'removed' : 0,
                                  'completed' : 0,
                                  'held' : 0,
                                  'error': 0},
                   "<queue2>" : { 'unsub' : 0,
                                  'idle' : 10,
                                  'running' : 5,
                                  'removed' : 0,
                                  'completed' : 0,
                                  'held' : 0,
                                  'error': 0},
                }
        '''

        self.log.debug('Starting')

        info = {}

        ### BEGIN TEST ###
        import autopyfactory.info2 
        group_by_queue = autopyfactory.info2.GroupByKey('match_apf_queue')

        mappings = self.factory.mappingscl.section2dict('CONDORBATCHSTATUS-JOBSTATUS2INFO')
        group_by_jobstatus = autopyfactory.info2.GroupByKeyRemap('jobstatus', mappings)

        algorithm = autopyfactory.info2.Algorithm()
        algorithm.add(group_by_queue)
        algorithm.add(group_by_jobstatus)
        algorithm.add(autopyfactory.info2.Length())
        
        out = apfqueue.batchstatus_plugin.getInfo(algorithm)
        ### END TEST ###
         
        for apfqueue in self.apfqueues.values():
            apfqname = apfqueue.apfqname
            info[apfqname] = {}
            self.log.info('calling getInfo() for queue %s' %apfqname)

            ### BEGIN TEST ###
            #qinfo = apfqueue.batchstatus_plugin.getInfo(apfqname)
            #info[apfqname]['running'] = qinfo.running
            #info[apfqname]['idle']    = qinfo.pending
            # info[apfqname]['held']    = qinfo.held? how to get this info?

            try:
                running = out.get(apfqname, 'running')
            except Exception:
                running = 0
            info[apfqname]['running'] = running

            try:
                idle = out.get(apfqname, 'idle')
            except Exception:
                idle = 0
            info[apfqname]['idle'] = idle

            ### END TEST ###
                
        self.log.info('Returning with info object %s' %info)
        return info


    def updateRequests(self, newinfo):
        '''
        prepares to update InfoService with new batch queue status

        we loop over Requests, updating each one individually.
        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'

        :param dict newinfo: dictionary with number of jobs "running", "idle", ... for each APFQueue
        '''

        self.log.debug('Starting')

        try:
            requests_l = self.vc3api.listRequests()
            for request in requests_l:
                self.log.info('Updating request = %s' %request.name)
                self.updateRequest(request, newinfo)
        except InfoConnectionFailure:
            self.log.warning('Could not connect to infoservice to update status of requests.')

        self.log.debug('Leaving')


    def updateRequest(self, request, newinfo):
        '''
        updates InfoService with a modified Request object
        with information from batch queue status plugins

        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
    
        :param Request request: a Request Entity object
        :param dict newinfo: dictionary with number of jobs "running", "idle", ... for each APFQueue
        '''

        self.log.debug('Starting for request %s with info %s' %(request, newinfo))

        statusraw = {}
        factoryid = self.factory.factoryid
        statusraw[factoryid] = {}

        # adding new info
        for qname, info in newinfo.items():
            self.log.debug('qname = %s, info =%s' %(qname, info))

            try:
                requestname, nodeset, username, resourcename = qname.split('.')
                self.log.debug('requestname = %s, nodeset = %s, username =%s, resourcename =%s' %(requestname, nodeset, username, resourcename))

                if requestname == request.name:
                    self.log.debug('proceeding with requestname %s' %(requestname))
                    if nodeset not in statusraw[factoryid].keys():
                        self.log.debug('adding nodeset %s to statusraw[%s] dictionary' %(nodeset, factoryid))
                        statusraw[factoryid][nodeset] = {}
                    statusraw[factoryid][nodeset][qname] = info

            except ValueError:
                self.log.warning("Malformed queue name: '%s'. Status update will not be performed." % (qname,))


        # recording new info
        request.statusraw = statusraw
        self.log.info('Updating Request object %s with new info %s' % (request.name, 
                                                                       request.statusraw))
        self.vc3api.storeRequest(request)     

        self.log.debug('Leaving')


class VC3(object):
      
    # for now, we deal with it as a true Singleton
    instance = None

    def __new__(cls, *k, **kw):
        if not VC3.instance:
            VC3.instance = _vc3(*k, **kw)
        return VC3.instance
        
