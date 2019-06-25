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

from vc3client.client import VC3ClientAPI
from vc3infoservice.infoclient import  InfoMissingPairingException, InfoConnectionFailure

from autopyfactory.interfaces import MonitorInterface
from autopyfactory.interfaces import _thread

from libfactory.info import StatusInfo, IndexByKey, IndexByKeyRemap, Count, TotalRunningTimeFromRunningAndFinishedJobs, MissingKeyException



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
        processed_info_d = self.__getinfo()
        self.updateRequests(processed_info_d)
        self.log.debug('Leaving')


    def __getinfo(self):


        # 1. get all BatchStatus plugins
        batchstatus_plugin_l = []
        for apfqueue in self.apfqueues.values():
            bsp = apfqueue.batchstatus_plugin
            if bsp not in batchstatus_plugin_l:
                self.__new_query_attributes(bsp)
                batchstatus_plugin_l.append(bsp)

        # 2. get raw data
        raw = []
        for bsp in batchstatus_plugin_l:
            #raw += bsp.getnewInfo().getraw()
            #raw += bsp.getInfo().getraw()
            raw = bsp.getRawInfo()
        self.status_info = StatusInfo(raw)

        # 3. process raw data
        processed_info_d = self.__process_info(self.status_info)
        return processed_info_d

    
    def __new_query_attributes(self, batch_status_plugin):

        new_q_attr_l = []
        new_history_attr_l = []
        if 'holdreason' not in batch_status_plugin.condor_q_attribute_l:
            new_q_attr_l.append('holdreason')
        if 'enteredcurrentstatus' not in batch_status_plugin.condor_q_attribute_l:
            new_q_attr_l.append('enteredcurrentstatus')
        if 'remotewallclocktime' not in batch_status_plugin.condor_history_attribute_l:
            new_history_attr_l.append('remotewallclocktime')
        if 'remotewallclocktime' not in batch_status_plugin.condor_q_attribute_l:
            new_q_attr_l.append('remotewallclocktime')
        batch_status_plugin.add_query_attributes(new_q_attr_l, new_history_attr_l)
            

    def __process_info(self, status_info):
        """
        process in several ways the raw data from the BatchStatus plugins
        """
        length = Count()

        group_by_queue = IndexByKey('match_apf_queue')
        newinfo = status_info.indexby(group_by_queue)

        mappings = self.factory.mappingscl.section2dict('CONDORBATCHSTATUS-JOBSTATUS2INFO')
        group_by_jobstatus = IndexByKeyRemap('jobstatus', mappings)
        remapinfo = newinfo.indexby(group_by_jobstatus)
        remapinfo = remapinfo.process(length)

        nomappings = self.factory.mappingscl.section2dict('NATIVECONDORBATCHSTATUS')
        group_by_jobstatus_native = IndexByKeyRemap('jobstatus', nomappings)
        noremapinfo = newinfo.indexby(group_by_jobstatus_native)
        noremapinfo = noremapinfo.process(length) 

        group_by_holdreason = IndexByKey('holdreason')
        holdreason = newinfo.indexby(group_by_holdreason)
        holdreason = holdreason.process(length) 

        total_running_time_2 = TotalRunningTimeFromRunningAndFinishedJobs()
        running = newinfo.reduce(total_running_time_2)

        out_d = {'remapinfo': remapinfo, 
                 'noremapinfo': noremapinfo,
                 'holdreason': holdreason,
                 'running': running}
        return out_d




    def updateRequests(self, processed_info_d):
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
                self.updateRequest(request, processed_info_d)
        except InfoConnectionFailure:
            self.log.warning('Could not connect to infoservice to update status of requests.')

        self.log.debug('Leaving')


    def updateRequest(self, request, processed_info_d):
        '''
        updates InfoService with a modified Request object
        with information from batch queue status plugins

        We know which queue belongs to which request because
        the name of the queues are '<request_name>.<user>.<resource_name>'
    
        :param Request request: a Request Entity object
        :param dict processed_info_d: dictionary with outputs of processing raw data
        '''

        self.log.debug('Starting for request %s' %(request))

        statusraw = {}
        factoryid = self.factory.factoryid
        statusraw[factoryid] = {}

        # get processed info out of the dictionary
        remapinfo = processed_info_d['remapinfo']
        noremapinfo = processed_info_d['noremapinfo']
        holdreason = processed_info_d['holdreason']
        running = processed_info_d['running']

        # loop over queues
        for apfqueue in self.apfqueues.values():
            qname = apfqueue.apfqname
            self.log.debug('trying queue = %s' %qname)
        
            try:
                requestname, nodeset, username, resourcename = qname.split('.')
            except ValueError:
                self.log.warning("Malformed queue name: '%s'. Status update will not be performed." % (qname,))
            else:
                try:
                    self.log.debug('requestname = %s, nodeset = %s, username =%s, resourcename =%s' %(requestname, nodeset, username, resourcename))
                    if requestname == request.name:
                        self.log.debug('proceeding with requestname %s' %(requestname))
                        if nodeset not in statusraw[factoryid].keys():
                            self.log.debug('adding nodeset %s to statusraw[%s] dictionary' %(nodeset, factoryid))
                            statusraw[factoryid][nodeset] = {}
                        statusraw[factoryid][nodeset][qname] = {}

                        # 1. Aggregated jobstatus values
                        aggregated_info = {}
                        job_status_l = ['running', 'pending']
                        for status in job_status_l:
                            try:
                                if status == 'running':
                                    aggregated_info[status] = remapinfo.get(qname, status)
                                if status == 'pending':
                                    aggregated_info['idle'] = remapinfo.get(qname, status)
        
                            except Exception:
                                aggregated_info[status] = 0
                        statusraw[factoryid][nodeset][qname]['aggregated'] = aggregated_info 

                        # 2. Native jobstatus values
                        non_aggregated_info = {}
                        job_status_l = ['unexpanded', 'idle', 'running', 'removed', 'completed', 'held', 'submission_err']
                        for status in job_status_l:
                            try:
                                non_aggregated_info[status] = noremapinfo.get(qname, status)
                            except Exception:
                                non_aggregated_info[status] = 0
                        statusraw[factoryid][nodeset][qname]['native'] = non_aggregated_info 

                        # 3. Hold Reasons
                        statusraw[factoryid][nodeset][qname]['hold_reason'] = {}
                        for reason in holdreason.get(qname).keys():
                            statusraw[factoryid][nodeset][qname]['hold_reason'][reason] = holdreason.get(qname, reason)

                        # 4. total number of running hours
                        statusraw[factoryid][nodeset][qname]['runningtime'] = running.get(qname)

                except MissingKeyException, ex:
                    self.log.warning('detected MissingKey Exception with content "%s". Continuing.' %ex)

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
        
