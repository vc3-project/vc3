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
        #newinfo = self.getInfo()
        #self.updateRequests(newinfo)
        self.updateRequests()
        self.updateRequests()
        self.log.debug('Leaving')

#    def getInfo(self):
#        '''
#        get batch status info from each APFQueue
#        output looks like this:
#
#         info = {  "<queue1>" : { 'unsub' : 0,
#                                  'idle' : 10,
#                                  'running' : 5,
#                                  'removed' : 0,
#                                  'completed' : 0,
#                                  'held' : 0,
#                                  'error': 0},
#                   "<queue2>" : { 'unsub' : 0,
#                                  'idle' : 10,
#                                  'running' : 5,
#                                  'removed' : 0,
#                                  'completed' : 0,
#                                  'held' : 0,
#                                  'error': 0},
#                }
#        '''
#
#        self.log.debug('Starting')
#
#        info = {}
#
#        import autopyfactory.info2 
#        group_by_queue = autopyfactory.info2.GroupByKey('match_apf_queue')
#
#        mappings = self.factory.mappingscl.section2dict('CONDORBATCHSTATUS-JOBSTATUS2INFO')
#        group_by_jobstatus = autopyfactory.info2.GroupByKeyRemap('jobstatus', mappings)
#
#        algorithm = autopyfactory.info2.Algorithm()
#        algorithm.add(group_by_queue)
#        algorithm.add(group_by_jobstatus)
#        algorithm.add(autopyfactory.info2.Length())
#        
#        for apfqueue in self.apfqueues.values():
#            # the reason why, at least for now, we loop over queues
#            # and get a new InfoStatus object for each one of them,
#            # even thought it is probably the same output in all cases,
#            # is because we do not really know here how many different
#            # instances of BatchStatus plugin are there.
#            # So we have to loop over queues, instead of a single query
#            # that returns raw info and we aggregate it by queues in here
#            #
#            # Maybe an alternative could be to find out first the list of
#            # BatchStatus plugins, and then loop over them,
#            # get raw info from each one of them, merge those outputs, 
#            # and process the merge result here
#
#            out = apfqueue.batchstatus_plugin.getnewInfo(algorithm)
#            apfqname = apfqueue.apfqname
#            info[apfqname] = {}
#            self.log.info('calling getInfo() for queue %s' %apfqname)
#
#            try:
#                running = out.get(apfqname, 'running')
#            except Exception:
#                running = 0
#            info[apfqname]['running'] = running
#
#            try:
#                idle = out.get(apfqname, 'idle')
#            except Exception:
#                idle = 0
#            info[apfqname]['idle'] = idle
#
#                
#        self.log.info('Returning with info object %s' %info)
#        return info


    #def updateRequests(self, newinfo):
    def updateRequests(self):
        '''
        prepares to update InfoService with new batch queue status

        we loop over Requests, updating each one individually.
        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
        '''

        self.log.debug('Starting')

        try:
            requests_l = self.vc3api.listRequests()
            for request in requests_l:
                self.log.info('Updating request = %s' %request.name)
                #self.updateRequest(request, newinfo)
                self.updateRequest(request)
        except InfoConnectionFailure:
            self.log.warning('Could not connect to infoservice to update status of requests.')

        self.log.debug('Leaving')


    #def updateRequest(self, request, newinfo):
    def updateRequest(self, request):
        '''
        updates InfoService with a modified Request object
        with information from batch queue status plugins

        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
    
        :param Request request: a Request Entity object
        '''

        self.log.debug('Starting for request %s' %(request))

        statusraw = {}
        factoryid = self.factory.factoryid
        statusraw[factoryid] = {}

        #### adding new info
        ###for qname, info in newinfo.items():
        ###    self.log.debug('qname = %s, info =%s' %(qname, info))
        ###
        ###    try:
        ###        requestname, nodeset, username, resourcename = qname.split('.')
        ###        self.log.debug('requestname = %s, nodeset = %s, username =%s, resourcename =%s' %(requestname, nodeset, username, resourcename))
        ###
        ###        if requestname == request.name:
        ###            self.log.debug('proceeding with requestname %s' %(requestname))
        ###            if nodeset not in statusraw[factoryid].keys():
        ###                self.log.debug('adding nodeset %s to statusraw[%s] dictionary' %(nodeset, factoryid))
        ###                statusraw[factoryid][nodeset] = {}
        ###            statusraw[factoryid][nodeset][qname] = {}
        ###            statusraw[factoryid][nodeset][qname]['aggregated'] = info
        ### 
        ###    except ValueError:
        ###        self.log.warning("Malformed queue name: '%s'. Status update will not be performed." % (qname,))
        ###
        #### recording new info
        ###request.statusraw = statusraw
        ###self.log.info('Updating Request object %s with new info %s' % (request.name, 
        ###                                                               request.statusraw))
        ###self.vc3api.storeRequest(request)     
        ###
        ###self.log.debug('Leaving')


        # FIXME:
        # This should be done only once
        import autopyfactory.info2 
        group_by_queue = autopyfactory.info2.GroupByKey('match_apf_queue')
        mappings = self.factory.mappingscl.section2dict('CONDORBATCHSTATUS-JOBSTATUS2INFO')
        group_by_jobstatus = autopyfactory.info2.GroupByKeyRemap('jobstatus', mappings)
        nomappings = self.factory.mappingscl.section2dict('NATIVECONDORBATCHSTATUS')
        group_by_jobstatus_native = autopyfactory.info2.GroupByKeyRemap('jobstatus', nomappings)
        length = autopyfactory.info2.Length()

        for apfqueue in self.apfqueues.values():
            qname = apfqueue.apfqname
            self.log.debug('trying queue = %s' %qname)

            try:
                requestname, nodeset, username, resourcename = qname.split('.')
            except ValueError:
                self.log.warning("Malformed queue name: '%s'. Status update will not be performed." % (qname,))
            else:
                self.log.debug('requestname = %s, nodeset = %s, username =%s, resourcename =%s' %(requestname, nodeset, username, resourcename))
                if requestname == request.name:
                    self.log.debug('proceeding with requestname %s' %(requestname))
                    if nodeset not in statusraw[factoryid].keys():
                        self.log.debug('adding nodeset %s to statusraw[%s] dictionary' %(nodeset, factoryid))
                        statusraw[factoryid][nodeset] = {}
                    statusraw[factoryid][nodeset][qname] = {}

                    # FIXME
                    # this query should be done only once per BatchStatus plugin
                    info = apfqueue.batchstatus_plugin.getnewInfo()
                    newinfo = info.group(group_by_queue)

                    remapinfo = newinfo.group(group_by_jobstatus)
                    remapinfo = remapinfo.reduce(length)
                    aggregated_info = {}
                    job_status_l = ['running', 'pending']
                    for status in job_status_l:
                        try:
                            if status = 'running':
                                aggregated_info[status] = remapinfo.get(qname, status)
                            if status = 'pending':
                                aggregated_info['idle'] = remapinfo.get(qname, status)

                        except Exception:
                            aggregated_info[status] = 0
                    statusraw[factoryid][nodeset][qname]['aggregated'] = aggregated_info 

                    noremapinfo = newinfo.group(group_by_jobstatus_native)
                    noremapinfo = noremapinfo.reduce(length) 
                    non_aggregated_info = {}
                    job_status_l = ['unexpanded', 'idle', 'running', 'removed', 'completed', 'held', 'submission_err']
                    for status in job_status_l:
                        try:
                            non_aggregated_info[status] = noremapinfo.get(qname, status)
                        except Exception:
                            non_aggregated_info[status] = 0
                    statusraw[factoryid][nodeset][qname]['native'] = non_aggregated_info 

        request.statusraw = statusraw
        self.log.info('Updating Request object %s with new info %s' % (request.name, 
                                                                       request.statusraw))
        self.vc3api.storeRequest(request)     
        
        self.log.debug('Leaving')




class VC3_2(object):
      
    # for now, we deal with it as a true Singleton
    instance = None

    def __new__(cls, *k, **kw):
        if not VC3_2.instance:
            VC3_2.instance = _vc3(*k, **kw)
        return VC3_2.instance
        
