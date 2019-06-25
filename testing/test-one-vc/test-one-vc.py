#!/usr/bin/env python

from __future__ import print_function

import logging
import sys
import traceback
import time
import subprocess
from datetime import datetime, timedelta

from ConfigParser import ConfigParser

import vc3infoservice
from vc3client.client import VC3ClientAPI

logging.basicConfig(level=logging.WARN)

class VCTester(object):
    def __init__(self, owner, project, allocation, node_number = 1, app_type = 'htcondor', vc_name_postfix = 'vc3-test-check', conf = '/etc/vc3/vc3-client.conf', headnode_user = 'vc3admin', headnode_key = '/etc/vc3/keys/key-to-init-headnodes'): 

        self.owner       = owner
        self.project     = project
        self.allocation  = allocation
        self.node_number = node_number
        self.name        = '-'.join([self.owner, vc_name_postfix])
        self.app_type    = 'htcondor'

        self.conf = ConfigParser()
        self.conf.read([conf])

        self.headnode_user = headnode_user
        self.headnode_key  = headnode_key
        
        self.client = client = VC3ClientAPI(self.conf)
        
        self._execute_status(silent = True)

    def __call__(self, command, *args):
        commands = "status start stop delete remote send receive condor auto".split()
        with_args = "remote send receive condor".split()
        if command not in commands:
            logging.error("Command should be one of {}".format(', '.join(commands)))
            return False

        if command in with_args:
            return getattr(self, '_execute_' + command)(*args)
        else:
            if len(args) > 0:
                logging.warn("Ignoring {} extra argument(s): {}".format(len(args), ','.join(args)))
            return getattr(self, '_execute_' + command)()

    def _execute_status(self, silent = False):
        self.request  = None
        self.headnode = None

        try:
            self.request = self.client.getRequest(self.name)
            if not silent:
                print("State: {}".format(self.request.state))
                print("Reason: {}".format(self.request.state_reason))
        except vc3infoservice.core.InfoEntityMissingException:
            logging.error("There is no active request named {}".format(self.name))
            return False

        try:
            if self.request.state not in ['new', 'initializing', 'failure', 'terminated']:
                self.headnode = self.client.getNodeset(self.request.headnode)
        except Exception as e:
            logging.warn("Could not find headnode info for {}: {}".format(self.name, e))

        return True

    def _execute_start(self):
        if self.request:
            logging.warn("Request {} already defined.".format(self.name))
            return True

        print("Creating nodeset {}, for {}, with {} workers...".format(self.name, self.app_type, self.node_number))

        nodeset = self.client.defineNodeset(name=self.name, owner=self.owner, node_number=self.node_number, app_type=self.app_type, app_role='worker-nodes', app_killorder = 'newest', displayname=self.name)

        cluster = self.client.defineCluster(name=self.name, owner=self.owner, nodesets=[nodeset.name], displayname=self.name)
        expiration = (datetime.utcnow() + timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S") 

        request = self.client.defineRequest(name=self.name, owner=self.owner, cluster=self.name, project=self.project, allocations=[self.allocation], environments=None, policy=None, expiration=expiration, displayname=self.name)

        try:
            self.client.storeRequest(request)
            self.client.storeCluster(cluster)
            self.client.storeNodeset(nodeset)
        except Exception as E:
            raise E

    def _execute_stop(self, *args):
        if self.request is None:
            logging.error("There is no active request named {}".format(self.name))
            return False
        if self.request.state == 'terminated':
            logging.warn("Request '{}' has been terminated already.".format(self.name))
            return False
        elif self.request.action == 'terminate':
            logging.warn("Request '{}' is already being terminated.".format(self.name))
            return False
        else:
            self.request.action = 'terminate'
            self.client.storeRequest(self.request)
            print("requesting '{}' to be terminated.".format(self.name))
            return True

    def _execute_remote(self, *args):
        if self.headnode is None:
            logging.error("Headnode for {} is still unknown".format(self.name))
            return False

        try:
            output   = subprocess.check_call(['ssh',
                    '-o',
                    'UserKnownHostsFile=/dev/null',
                    '-o',
                    'StrictHostKeyChecking=no',
                    '-o',
                    'ConnectTimeout=10',
                    '-i',
                    self.headnode_key,
                    '-l',
                    self.headnode_user,
                    self.headnode.app_host,
                    '--'] + list(args))
            return True
        except subprocess.CalledProcessError as e:
            logging.error("Remote command '{}' had a non-zero exit status: {}".format(' '.join(args), e.returncode))
            return False
        except Exception as e:
            logging.error("Remote execution had an unexpected error: {}".format(e))
            return False

    def _execute_delete(self):
        for m in ['deleteRequest', 'deleteCluster', 'deleteNodeset']:
            try:
                getattr(self.client,m)(self.name)
            except vc3infoservice.core.InfoEntityMissingException:
                pass
        return True

    def _execute_auto(self):
        try:
            self('start')
            self.wait_for_states(states = ['pending', 'running'])
            self('remote', 'uptime')
            self.wait_for_states(states = ['running'])
            self._execute_condor('/bin/uname', '-a')
            #self('stop')
            self.wait_for_states(states = ['terminated'], cycle_len = 1, max_wait=1)
            return True
        except TimeoutState as e:
            logging.error('cluster never reached any of the state(s): {}'.format(','.join(e.states)))
        except Exception as e:
            logging.error('unexpected error: {}'.format(e))
        finally:
            if self.request and self.request.state == 'terminated':
                self('delete')
            else:
                logging.warn("not deleting request {}, as it is in state '{}'".format(self.request.name, self.request.state))

        return False
        

    def wait_for_states(self, states, cycle_len=60, max_wait=600):
        total_time = 0
        
        if(cycle_len < 1):
            raise TypeError("cycle_len must be a positive integer: {}".format(cycle_len))

        while(max_wait > total_time):
            self._execute_status(silent = True)
            if self.request and self.request.state in states:
                return True
            time.sleep(cycle_len)
            total_time += cycle_len
        
        raise TimeoutState(states = states, max_wait = max_wait)

    def transfer_file(self, filename_src, filename_dest):
        try:
            output   = subprocess.check_call(['scp',
                    '-q',
                    '-o', 'LogLevel=error',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'ConnectTimeout=10',
                    '-i', self.headnode_key,
                    filename_src, 
                    filename_dest])
            return True
        except subprocess.CalledProcessError as e:
            logging.error("Remote command scp had a non-zero exit status: {}".format(e.returncode))
            return False
        except Exception as e:
            logging.error("Remote execution had an unexpected error: {}".format(self.name, e))
            return False


    def _execute_send(self, filename_src, filename_dest = None):
        if self.headnode is None:
            logging.error("Headnode for {} is still unknown".format(self.name))
            return False
        filename_dest = filename_dest or filename_src
        filename_dest = self.headnode_user + '@' + self.headnode.app_host + ':' + filename_dest
        return self.transfer_file(filename_src, filename_dest)

    def _execute_receive(self, filename_src, filename_dest = None):
        if self.headnode is None:
            logging.error("Headnode for {} is still unknown".format(self.name))
            return False
        filename_dest = filename_dest or filename_src
        filename_src = self.headnode_user + '@' + self.headnode.app_host + ':' + filename_src
        return self.transfer_file(filename_src, filename_dest)

    def _execute_condor(self, command, *args):
        sfile = self.name + '.submit'
        with open(sfile, 'w') as f:
            f.write("""
universe = vanilla
executable = {cmd}
arguments = {args}
output = {name}.out
error  = {name}.err
log = {name}.log
should_transfer_files = yes
transfer_executable   = yes
when_to_transfer_output = on_exit
queue 1
""".format(name = self.name, cmd = command, args = ' '.join(args)))
        if not self('send', sfile):
            logging.error('could not transfer condor submit file to headnode')
            return False

        if not self('remote', 'condor_submit', sfile):
            logging.error('error while submiting condor job')
            return False

        if not self('remote', 'condor_wait', '-wait', str(60), self.name + '.log'):
            logging.error('condor job did not finish in the alloted time')
            return False

        for ext in 'out err log'.split():
            filename = self.name + '.' + ext
            if not self('receive', filename):
                logging.error('could not transfer file from headnode: {}'.format(filename))
                return False

        print('-------start of output---------')
        with open(self.name + '.out') as f:
            for l in f:
                sys.stdout.write(l)
        print('--------end of output----------')


class TimeoutState(Exception):
    def __init__(self, states, max_wait):
        message = "Did not reach state(s) '{}' in {} seconds.".format(','.join(states), max_wait)
        super(TimeoutState, self).__init__(message)
        self.states = states
        self.max_wait = max_wait

if __name__ == '__main__':
    command = None
    try:
        command = sys.argv[1]
    except:
        command = 'status'
        raise 
    
    tester = VCTester(owner = 'btovar', project = 'btovar', allocation = 'btovar.ndccl')
        
    result = tester(command, *sys.argv[2:])

    sys.exit(result != True)

#vim: set sts=4 sw=4 ts=4 expandtab ft=python:

