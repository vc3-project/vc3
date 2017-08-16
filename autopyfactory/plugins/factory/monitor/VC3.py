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
        self._thread_loop_interval = 30 # FIXME !!


        self.vc3clientconf = config.generic_get('Factory',
                                                'monitor.vc3.vc3clientconf',
                                                default_value=os.path.expanduser('~/.vc3/vc3-client.conf'))

        self.log.debug("config to contact the InfoService is %s" % self.vc3clientconf )
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

        self.log.debug('starting')

        info = {}
         
        for apfqueue in self.apfqueues:
            apfqname = apfqueue.apfqname
            self.log.info('calling getInfo() for queue %s' %apfqname)
            qinfo = apfque.batchstatus_plugin.getInfo(apfqname)
            info['apfqname']['running'] = qinfo.running
            info['apfqname']['idle'] = qinfo.pending
                
        self.log.info('returning with info object %s' %info)
        return info


    def updateRequests(self, newinfo):
        '''
        prepares to update InfoService with new batch queue status

        we loop over Requests, updating each one individually.
        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
        '''

        self.log.debug('Starting')
        requests_l = self.vc3api.listRequests()
        for request in requests_l:
            self.log.info('updating request = %s' %request.name)
            self.updateRequest(request, newinfo)
        self.log.debug('Leving')


    def updateRequest(self, request, newinfo):
        '''
        updates InfoService with a modified Request object
        with information from batch queue status plugins

        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
        '''

        self.log.debug('Starting')

        statusraw = {}
        factoryid = self.factory.factoryid
        statusraw[factoryid] = {}

        # adding new info
        for qname, info in newinfo.items():
            requestname, nodeset, username, resourcename = qname.split('.')
            if requestname == request.name:
                if nodeset not in statusraw[factoryid].keys():
                    statusraw[factoryid][nodeset] = {}
                    statusraw[factoryid][nodeset][qname] = info

        # recording new info
        self.log.info('updating Request object %s with new info %s' \
                                               %(request.name, 
                                                 request.statusraw))
        request.statusraw = statusraw
        self.vc3api.storeRequest(request)     

        self.log.debug('Leaving')


  



#    def registerFactory(self, apfqueue):
#        """
#        Initial startup hello message from new factory...
#        
#        """
#        self.log.debug("registerFactory( apfqueue = %s) called." % apfqueue)
#        return None
#    
#    
#    def sendMessage(self, text):
#        """
#        Send message to monitor, if it supports this function. 
#        """
#        self.log.debug("sendMessage( text=%s) called." % text)
#    
#    
#    def updateJobs(self, jobinfolist ):
#        """
#        Update information about job/jobs. 
#        Should support either single job object or list of job objects.  
#         
#        """
#        self.log.debug("updateJobs(jobinfolist=%s) called." % jobinfolist )
#        return None
#   
#    def registerJobs(self, apfqueue, jobinfolist ):
#        """
#        Update information about job/jobs. 
#        Should support either single job object or list of job objects.  
#         
#        """
#        self.log.debug("registerJobs(apfqueue=%s, jobinfolist=%s) called." % ( apfqueue, jobinfolist))
#        return None   
#    
#    def updateLabel(self, label, msg):
#        """
#        Update label. 
#        Should support either single job object or list of job objects.  
#         
#        """
#        self.log.debug("updateLabel(label=%s, msg=%s) called." % (label, msg))
#        return None       
        


class VC3(object):
      
    # for now, we deal with it as a true Singleton
    instance = None

    def __new__(cls, *k, **kw):
        if not VC3.instance:
            VC3.instance = _vc3(*k, **kw)
        return VC3.instance
        
