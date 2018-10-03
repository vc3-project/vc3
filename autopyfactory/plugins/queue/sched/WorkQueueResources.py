#! /usr/bin/env python
#

from autopyfactory.interfaces import SchedInterface

import logging
import math

class WorkQueueResources(SchedInterface):
    id = 'workqueue'
    
    def __init__(self, apfqueue, config, section):
        try:
            self.apfqueue = apfqueue
            self.apfqname = apfqueue.apfqname

            self.log = logging.getLogger("main.schedplugin[%s]" % self.apfqname)

            self.worker = {}

            self.worker['cores']  = self.apfqueue.qcl.generic_get(self.apfqname, 'workqueue.cores',  'getint', default_value = 1)
            self.worker['memory'] = self.apfqueue.qcl.generic_get(self.apfqname, 'workqueue.memory', 'getint', default_value = 512)
            self.worker['disk']   = self.apfqueue.qcl.generic_get(self.apfqname, 'workqueue.disk',   'getint', default_value = 512)

            self.log.trace("SchedPlugin: Object initialized.")
        except Exception, ex:
            self.log.error("SchedPlugin object initialization failed. Raising exception")
            raise ex


    def calcSubmitNum(self, n=0):
        """ 
        It just returns nb of Activated Jobs - nb of Pending Pilots
        """
        out = n

        self.log.trace('Starting.')
        self.wmsqueueinfo = self.apfqueue.wmsstatus_plugin.getInfo(queue = self.apfqueue.wmsqueue, maxtime = self.apfqueue.wmsstatusmaxtime)
        #self.queueinfo = self.apfqueue.batchstatus_plugin.getInfo(queue = self.apfqueue.apfqname, maxtime = self.apfqueue.batchstatusmaxtime)
        self.queueinfo = self.apfqueue.batchstatus_plugin.getOldInfo(queue = self.apfqueue.apfqname, maxtime = self.apfqueue.batchstatusmaxtime)

        if self.wmsqueueinfo is None or self.queueinfo is None:
            self.log.warning("Missing info. wmsinfo is %s batchinfo is %s. Return=0" % (self.wmsqueueinfo, self.queueinfo))
            out = 0 
            msg = 'Invalid wmsinfo or batchinfo' 
        else:
            (out, msg) = self._calc(n)
        return (out, msg)

    def _calc(self, input):
        '''
        algorithm 
        '''
        pending_pilots = self.queueinfo.pending
        running_pilots = self.queueinfo.running

        try:
            by_cores   = self._split_resources(self.worker['cores'], self.wmsqueueinfo.cores_total, self.wmsqueueinfo.cores_inuse, self.wmsqueueinfo.cores_waiting)
            by_memory = self._split_resources(self.worker['memory'], self.wmsqueueinfo.memory_total, self.wmsqueueinfo.memory_inuse, self.wmsqueueinfo.memory_waiting)
            by_disk   = self._split_resources(self.worker['disk'], self.wmsqueueinfo.disk_total, self.wmsqueueinfo.disk_inuse, self.wmsqueueinfo.disk_waiting)

            activated_jobs = min(self.wmsqueueinfo.ready, max(by_cores, by_memory, by_disk))
        except:
            activated_jobs = self.wmsqueueinfo.ready

        self.log.trace("pending = %s running = %s" % (pending_pilots, running_pilots))
        out = activated_jobs - pending_pilots

        msg = "WorkQueueResources:in=%s;activated=%d,pending=%d;ret=%d;by_cores=%d;by_memory=%d;by_disk=%d" % (input, activated_jobs, pending_pilots, out, by_cores, by_memory, by_disk)
        self.log.info(msg)
        return (out,msg)


    def _split_resources(self, per_worker, total, inuse, waiting):
        needed  = inuse + waiting
        missing = needed - total
        pilots_missing = int(max(0, math.ceil(missing/per_worker)))

        return pilots_missing

