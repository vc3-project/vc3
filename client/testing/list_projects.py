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
    default_conf = "/etc/vc3/vc3-client.conf"
    if 'VC3_SERVICES_HOME' in os.environ:
        default_conf = os.path.join(os.environ['VC3_SERVICES_HOME'], 'etc', 'vc3-client.conf') + ',' + default_conf
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

    project_1 = client.defineProject('PROJECT_1', 'calvin',    ['hobbes', 'waldo'])
    project_2 = client.defineProject('PROJECT_2', 'calvin',    ['hobbes'])
    project_3 = client.defineProject('PROJECT_3', 'scoobydoo', [])

    client.storeProject(project_1)
    client.storeProject(project_2)
    client.storeProject(project_3)

    print 'Projects owned by calvin:'
    print [ p.name for p in client.getProjectsOfOwner('calvin') ]

    print 'Projects owned by scoobydoo:'
    print [ p.name for p in client.getProjectsOfOwner('scoobydoo') ]

    print 'Projects with hobbes as a member:'
    print [ p.name for p in client.getProjectsOfUser('hobbes') ]


