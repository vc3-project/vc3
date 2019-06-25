from optparse import OptionParser
from ConfigParser import ConfigParser

import base64
import logging
import os
import time

from vc3client.client import VC3ClientAPI

if __name__ == '__main__':

    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    parser = OptionParser(usage='%prog [OPTIONS]')
    default_conf = "/etc/vc3/vc3-master.conf"
    if 'VC3_SERVICES_HOME' in os.environ:
        default_conf = os.path.join(os.environ['VC3_SERVICES_HOME'], 'etc', 'vc3-master.conf') + ',' + default_conf
        parser.add_option("--conf", dest="confFiles",
                default=default_conf,
                action="store",
                metavar="FILE1[,FILE2,FILE3]",
                help="Load configuration from FILEs (comma separated list)")

    (options, args) = parser.parse_args()

    log.info("Reading conf files: '%s'" % options.confFiles)
    config = ConfigParser()
    config.read(options.confFiles.split(','))

    client = VC3ClientAPI(config)


    resource_1   = client.defineResource(name = 'RESOURCE_1', owner = 'Waldo', accesstype = 'batch', accessmethod = 'ssh', accessflavor = 'strawberry', accesshost = 'resource.org', accessport = '1234', gridresource = None, mfa = False)
    resource_2   = client.defineResource(name = 'RESOURCE_2', owner = 'Waldo', accesstype = 'batch', accessmethod = 'ssh', accessflavor = 'strawberry', accesshost = 'otherresource.org', accessport = '1234', gridresource = None, mfa = False)

    allocation_1 = client.defineAllocation(name = 'ALLOCATION_1', owner = 'Waldo', resource = 'RESOURCE_1', accountname = 'vc3-waldo')
    allocation_2 = client.defineAllocation(name = 'ALLOCATION_2', owner = 'Waldo', resource = 'RESOURCE_2', accountname = 'vc3-waldo')

    environment_1 = None
    with open('file-to-stage', 'r') as f:
        data = f.read()
        environment_1 = client.defineEnvironment(name = 'ENVIRONMENT_1', owner = 'Waldo', packagelist = ['cctools'], files = {'my_file' : client.encode(data)})

    node_set_1 = client.defineNodeset(name = 'NODE_SET_1', owner = 'Waldo', app_type = 'APP_TYPE', app_role = 'APP_ROLE', node_number = 10, environment = 'ENVIRONMENT_1')

    cluster_1  = client.defineCluster(name = 'CLUSTER_1', owner = 'Waldo', nodesets = ['NODE_SET_1'])

    r = client.defineRequest(name = 'REQUEST_1', owner = 'Waldo', cluster = 'CLUSTER_1', allocations = ['ALLOCATION_1', 'ALLOCATION_2'], policy = None, expiration = None)

    client.storeAllocation(allocation_1)
    client.storeAllocation(allocation_2)
    client.storeResource(resource_1)
    client.storeResource(resource_2)
    client.storeEnvironment(environment_1)
    client.storeNodeset(node_set_1)
    client.storeCluster(cluster_1)
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'validated':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to validate request')
            time.sleep(2)
        else:
            break

    log.info('contents of queues.conf:\n%s\n', base64.b64decode(r.queuesconf))
    log.info('contents of auth.conf:\n%s\n', base64.b64decode(r.authconf))

    log.info('simulating factory configuration')
    r.statusinfo = {'NODE_SET_1' : {'running' : 0, 'idle' : 0}};
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'pending':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to observe configured factory')
            time.sleep(2)
        else:
            break
    
    log.info('simulating that factory started working')
    r.statusinfo = {'NODE_SET_1' : {'running' : 5, 'idle' : 0}};
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'growing':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to observe some factory work')
            time.sleep(2)
        else:
            break

    log.info('simulating that factory fullfilled request')
    r.statusinfo = {'NODE_SET_1' : {'running' : 10, 'idle' : 0}};
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'running':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to observe all factory work')
            time.sleep(2)
        else:
            break

    log.info('simulating terminate command from webportal')
    r.action = 'terminate'
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'shrinking':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to observe terminate action')
            time.sleep(2)
        else:
            break

    log.info('simulating factory terminated request')
    r.statusinfo = {'NODE_SET_1' : {'running' : 0, 'idle' : 0}};
    client.storeRequest(r)

    while True:
        r = client.getRequest('REQUEST_1')

        if r.state != 'terminated':
            log.info('Current request state: %s (%s)' % (r.state, str(r.state_reason)))
            log.info('Waiting for master to terminate request')
            time.sleep(2)
        else:
            break

