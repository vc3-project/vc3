#!/bin/env python
#
# AutoPyfactory batch plugin for WorkQueue running on a local Condor
#

import os
import sys

from CondorLocal import CondorLocal 
from autopyfactory import jsd


class WorkQueueCondor(CondorLocal):
    id = 'workqueuecondor'
    
    def __init__(self, apfqueue, config, section):

        qcl = config             

        newqcl = qcl.clone()
        super(WorkQueueCondor, self).__init__(apfqueue, newqcl, section) 

        self.arguments_original  = self.arguments

        self.catalog_name_file = newqcl.generic_get(self.apfqname, 'workqueue.catalog_name_file', default_value = None)
        self.catalog_port_file = newqcl.generic_get(self.apfqname, 'workqueue.catalog_port_file', default_value = None)

        if self.catalog_name_file and not self.catalog_name_file:
            raise Exception('Port file specified without a hostname file')

        self.executable = os.path.expandvars(self.executable)
        if(self.catalog_name_file):
            self.catalog_name_file = os.path.expandvars(self.catalog_name_file)
        if(self.catalog_port_file):
            self.catalog_port_file = os.path.expandvars(self.catalog_port_file)

        self.log.info('WorkQueueCondor: Object initialized.')


    def submit(self, n):

        catalog = None
        m = n
        if self.catalog_name_file:
            try:
                f = open(self.catalog_name_file, 'r')
                catalog = f.readline()
            except IOError:
                self.log.info('Name of catalog in ' + self.catalog_name_file + ' not available.')
                m = 0

        if self.catalog_port_file:
            try:
                f = open(self.catalog_name_file, 'r')
                port = f.readline()
                catalog = catalog + ':' + port
            except IOError:
                self.log.info('Port number in ' + self.catalog_port_file + ' not available.')
                m = 0

        if n > 0 and m == 0:
            self.log.info('No catalog information found. No jobs will be submitted.')

        return super(WorkQueueCondor, self).submit(m)




