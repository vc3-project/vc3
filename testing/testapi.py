#!/bin/env python

import ast
import base64
import json
import logging
import os
import sys
import yaml
import StringIO
import ConfigParser

from entities import User, Project, Resource, Allocation, Nodeset, Request, Cluster, Environment
from vc3client import VC3ClientAPI
from vc3infoservice import infoclient
from vc3infoservice.core import  InfoMissingPairingException, InfoConnectionFailure, InfoEntityExistsException, InfoEntityMissingException, InfoEntityUpdateMissingException


def setuplogging():
    log = logging.getLogger()
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    formatter = logging.Formatter(FORMAT)
    #formatter.converter = time.gmtime  # to convert timestamps to UTC
    logStream = logging.StreamHandler()
    logStream.setFormatter(formatter)
    log.addHandler(logStream)

    log.setLevel(logging.WARN)
    if results.debug:
        log.setLevel(logging.DEBUG)
    if results.verbose:
        log.setLevel(logging.INFO)
    log.info('Logging initialized.')


if __name__ == '__main__':
    setuplogging()

    try:
        cp = ConfigParser()
        self.log.info("Config string is %s" % ns.configpath)
        configpaths = ns.configpath.split(',')
        configfiles = []
        for p in configpaths:
            p = p.strip()
            configfiles.append(os.path.expanduser(p))
        readfiles = cp.read(configfiles)
        self.log.info('Read config files %s' % readfiles)
        capi = VC3ClientAPI(cp)
    except Exception:
            print(traceback.format_exc(None))
            sys.exit(1) 
            