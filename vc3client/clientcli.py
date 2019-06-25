#!/usr/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import argparse
import base64
import logging
import os
import sys
import traceback
import warnings


from ConfigParser import ConfigParser
from client import VC3ClientAPI
from vc3infoservice.core import  InfoMissingPairingException, InfoConnectionFailure, InfoEntityExistsException, InfoEntityMissingException, InfoEntityUpdateMissingException


class VC3ClientCLI(object):
    '''
    
    '''
    def __init__(self):
        self.parseopts()
        self.setuplogging()

    def parseopts(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', 
                            action="store", 
                            dest='configpath', 
                            default=','.join(['/etc/vc3/vc3-client.conf', os.path.expanduser('~/.local/etc/vc3-client.conf'), os.path.expanduser('~/.local/etc/vc3-client-local.conf')]),
                            help='configuration file path.')
        
        parser.add_argument('-d', '--debug', 
                            action="store_true", 
                            dest='debug', 
                            help='debug logging')        

        parser.add_argument('-v', '--verbose', 
                            action="store_true", 
                            dest='verbose', 
                            help='verbose/info logging')            
        
        # Init sub-command
        ########################### User ##########################################
        subparsers = parser.add_subparsers( dest="subcommand")

        parser_usercreate = subparsers.add_parser('user-create', 
                                                help='create new vc3 user')
        parser_usercreate.add_argument('username', 
                                     action="store")
        
        parser_usercreate.add_argument('--firstname', 
                                     action="store", 
                                     dest="firstname",
                                     required=True
                                     )

        parser_usercreate.add_argument('--lastname', 
                                     action="store", 
                                     dest="lastname",
                                     required=True 
                                     )

        parser_usercreate.add_argument('--email', 
                                     action="store", 
                                     dest="email",
                                     required=True 
                                     )

        parser_usercreate.add_argument('--institution', 
                                     action="store", 
                                     dest="organization",
                                     required=True 
                                     )  
        
        parser_usercreate.add_argument('--identity_id', 
                                     action="store", 
                                     dest="identity_id", 
                                     default=None)
        
        
        # description, displayname,url, docurl 
        parser_usercreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_usercreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None
                                     )        

        parser_usercreate.add_argument('--sshpubstring', 
                                     action="store", 
                                     dest="sshpubstring",
                                     required=False,
                                     default=None
                                     )        

        parser_usercreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_usercreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     )          
        
        
        
        parser_userlist = subparsers.add_parser('user-list', 
                                                help='list vc3 user(s)')
        
        parser_userlist.add_argument('--username', 
                                     action="store")

        parser_userdelete = subparsers.add_parser('user-delete', 
                                                help='delete a vc3 user')
        parser_userdelete.add_argument('username', 
                                     action="store")
        
       
        ########################### Project ##########################################
        parser_projectcreate = subparsers.add_parser('project-create', 
                                                help='create new vc3 project')
        
        parser_projectcreate.add_argument('projectname', 
                                     action="store")

        parser_projectcreate.add_argument('--owner', 
                                     action="store", 
                                     dest="owner", 
                                     default='unknown')

        parser_projectcreate.add_argument('--members', 
                                     action="store", 
                                     dest="members", 
                                     default=None,
                                     help='comma-separated list of vc3users'
                                     )
        
        parser_projectcreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_projectcreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_projectcreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_projectcreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     )

        parser_projectcreate.add_argument('--organization', 
                                     action="store", 
                                     dest="organization",
                                     required=False,
                                     default=None 
                                     )

        parser_projectadduser = subparsers.add_parser('project-adduser', 
                                                help='add user to vc3 project')
        
        parser_projectadduser.add_argument('projectname', 
                                     action="store")

        parser_projectadduser.add_argument('user', 
                                     action="store", 
                                     )


        parser_projectremoveuser = subparsers.add_parser('project-removeuser', 
                help='remove user from vc3 project')
        
        parser_projectremoveuser.add_argument('projectname', 
                                     action="store")

        parser_projectremoveuser.add_argument('user', 
                                     action="store", 
                                     )


        parser_projectaddallocation = subparsers.add_parser('project-addallocation', 
                                                help='add allocation to vc3 project')

        parser_projectaddallocation.add_argument('projectname', 
                                     action="store")

        parser_projectaddallocation.add_argument('allocationname', 
                                     action="store", 
                                     )


        parser_projectremoveallocation = subparsers.add_parser('project-removeallocation', 
                                                help='remove allocation from vc3 project')

        parser_projectremoveallocation.add_argument('projectname', 
                                     action="store")

        parser_projectremoveallocation.add_argument('allocationname', 
                                     action="store", 
                                     )

              
        
        parser_projectlist = subparsers.add_parser('project-list', 
                                                help='list all vc3 project(s)')

        parser_projectlist.add_argument('--projectname', 
                                     action="store",
                                     dest='projectname',
                                     required=False, 
                                     help='list details of specified project',
                                     default=None)

        parser_projectdelete = subparsers.add_parser('project-delete', 
                                                help='delete a vc3 project')
        
        parser_projectdelete.add_argument('projectname', 
                                     action="store")


        ########################### Resource ##########################################
        parser_resourcecreate = subparsers.add_parser('resource-create', 
                                                help='create new vc3 resource')
        
        parser_resourcecreate.add_argument('resourcename',
                                           action="store")

        parser_resourcecreate.add_argument('--owner', 
                                     action="store", 
                                     dest="owner", 
                                    )

        parser_resourcecreate.add_argument('--accesstype', 
                                     action="store", 
                                     dest="accesstype",
                                     help="grid|remote-batch|local-batch|cloud", 
                                     )

        parser_resourcecreate.add_argument('--accessmethod', 
                                     action="store", 
                                     dest="accessmethod",
                                     help="ce|ssh|gsissh|local", 
                                     )

        parser_resourcecreate.add_argument('--accessflavor', 
                                     action="store", 
                                     dest="accessflavor",
                                     help="condor-ce|slurm|sge|ec2|nova|gce",  
                                     )

        parser_resourcecreate.add_argument('--accesshost', 
                                     action="store", 
                                     dest="accesshost",
                                     help="DNS fully qualified hostname",  
                                     )
        
        parser_resourcecreate.add_argument('--accessport', 
                                     action="store", 
                                     dest="accessport",
                                     help="22|9618|8773|etc..",  
                                     )

        parser_resourcecreate.add_argument('--accessgateway', 
                                     action="store", 
                                     dest="accessgateway",
                                     help="Hostname of intermediate host",  
                                     )


        parser_resourcecreate.add_argument('--nodeinfo', 
                                     action="store", 
                                     dest="nodeinfo",
                                     help="nodeinfo name with the size of nodes for this resource.",  
                                     )

        parser_resourcecreate.add_argument('--scratchdir', 
                                     action="store", 
                                     dest="scratchdir",
                                     help="root directory to which bosco/vc3-resource-manager writes data",
                                     default='/home/${USER}'
                                     )
        
        parser_resourcecreate.add_argument('--gridresource', 
                                     action="store", 
                                     dest="gridresource",
                                     help="e.g. http://cldext02.usatlas.bnl.gov:8773/services/Cloud, corigrid.nersc.gov/jobmanager-slurm ",  
                                     default=None
                                     )

        parser_resourcecreate.add_argument('--cloudspotprice', 
                                     action="store", 
                                     dest="cloudspotprice",
                                     help="spot price",
                                     default=None
                                     )

        parser_resourcecreate.add_argument('--cloudinstancetype', 
                                     action="store", 
                                     dest="cloudinstancetype",
                                     help="instance type",
                                     default=None
                                     )

        parser_resourcecreate.add_argument('--mfa', 
                                     action="store_true", 
                                     dest="mfa",
                                     help="requires multi-factor/OTP authentication",
                                     default=False, 
                                     )

        parser_resourcecreate.add_argument('--public', 
                                     action="store_true",
                                     dest="public",
                                     help="set visible to all users",
                                     default=False, 
                                     )

        parser_resourcecreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_resourcecreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_resourcecreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_resourcecreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     )

        parser_resourcecreate.add_argument('--pubtokendocurl', 
                                     action="store", 
                                     dest="pubtokendocurl",
                                     required=False,
                                     default=None 
                                     )

        parser_resourcecreate.add_argument('--organization', 
                                     action="store", 
                                     dest="organization",
                                     required=False 
                                     )                
                                        
        parser_resourcelist = subparsers.add_parser('resource-list', 
                                                help='list vc3 resource(s)')

        parser_resourcelist.add_argument('--resource',
                                         dest='resourcename', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified resource',
                                         default=None)

        parser_resourcedelete = subparsers.add_parser('resource-delete', 
                                                help='delete vc3 resource')
        
        parser_resourcedelete.add_argument('resourcename',
                                           action="store")

        ########################### Allocation  ##########################################
        parser_allocationcreate = subparsers.add_parser('allocation-create', 
                                                help='create new vc3 allocation')
        
        parser_allocationcreate.add_argument('allocationname', 
                                     action="store")

        parser_allocationcreate.add_argument('--owner', 
                                     action="store", 
                                     dest="owner", 
                                     )

        parser_allocationcreate.add_argument('--resource', 
                                     action="store", 
                                     dest="resource", 
                                     )

        parser_allocationcreate.add_argument('--accountname', 
                                     action="store", 
                                     dest="accountname", 
                                     )
        
        parser_allocationcreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_allocationcreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_allocationcreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_allocationcreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     )        
        
        parser_allocationcreate.add_argument('--pubtokendocurl', 
                                     action="store", 
                                     dest="pubtokendocurl",
                                     required=False,
                                     default=None 
                                     )

        parser_allocationcreate.add_argument('--privtoken', 
                                     action="store", 
                                     dest="privtoken",
                                     required=False,
                                     default=None 
                                     )
        
        parser_allocationlist = subparsers.add_parser('allocation-list', 
                                                help='list vc3 allocation(s)')

        parser_allocationlist.add_argument('--allocationname',
                                        action="store",
                                        required=False, 
                                        help='list details of specified allocation',
                                        default=None)

        parser_allocationgetpubtoken = subparsers.add_parser('allocation-getpubtoken', 
                                                help='print pub token')

        parser_allocationgetpubtoken.add_argument('--allocationname', 
                                        action="store",
                                        required=True,
                                        help='specify allocation')

        parser_allocationdelete = subparsers.add_parser('allocation-delete', 
                                                help='delete a vc3 allocation')
        
        parser_allocationdelete.add_argument('allocationname', 
                                     action="store")

        parser_allocationvalidate = subparsers.add_parser('allocation-validate', 
                                                help='Validate allocation.')

        parser_allocationvalidate.add_argument('--allocationname', 
                                        action="store",
                                        required=True,
                                        help='specify allocation')

        ########################### Nodeinfo  ##########################################
        parser_nodeinfocreate = subparsers.add_parser('nodeinfo-create',
                                                     help='create new nodeinfo specification')

        parser_nodeinfocreate.add_argument('--owner', 
                                          action="store", 
                                          dest="owner", 
                                          )

        parser_nodeinfocreate.add_argument('--cores', 
                                          help='number of cores per node',
                                          dest="cores",
                                          default=1,       # default assume 1 core
                                          action="store")

        parser_nodeinfocreate.add_argument('--memory_mb', 
                                          help='RAM in MB available per node',
                                          dest="memory_mb",
                                          default=1024,    # default assume 1GB
                                          action="store")

        parser_nodeinfocreate.add_argument('--storage_mb', 
                                          help='Storage in MB available per node',
                                          dest="storage_mb",
                                          default=1024,    # default assume 1GB
                                          action="store")

        parser_nodeinfocreate.add_argument('--native_os', 
                                          help='Native Operating System in nodeinfo',
                                          dest="native_os",
                                          default="Unknown",
                                          action="store")

        parser_nodeinfocreate.add_argument('--features', 
                                     action="store", 
                                     dest="features",
                                     default='',
                                     help="Comma-separated list of features this node type has (e.g., 'singularity', 'cvmfs', etc.).",  
                                     )


        parser_nodeinfocreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_nodeinfocreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_nodeinfocreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_nodeinfocreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     ) 

        parser_nodeinfocreate.add_argument('nodeinfoname', 
            help='name of the nodeinfo to be created',
            action="store")
      
        parser_nodeinfolist = subparsers.add_parser('nodeinfo-list', 
                                                help='list vc3 nodeinfo(s)')

        parser_nodeinfolist.add_argument('--nodeinfoname', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified nodeinfo',
                                         default=None)

        parser_nodeinfodelete = subparsers.add_parser('nodeinfo-delete',
                                                     help='delete a nodeinfo specification')

        parser_nodeinfodelete.add_argument('nodeinfoname',
                                           action="store")

        
        ########################### Nodeset  ##########################################
        parser_nodesetcreate = subparsers.add_parser('nodeset-create',
                                                     help='create new nodeset specification')

        parser_nodesetcreate.add_argument('--owner', 
                                          action="store", 
                                          dest="owner", 
                                          )

        parser_nodesetcreate.add_argument('--node_number', 
                                          help='number of nodes in nodeset',
                                          default=1,
                                          action="store")
      
        parser_nodesetcreate.add_argument('--app_type', 
                                          help='general middleware type of node',
                                          action="store")

        parser_nodesetcreate.add_argument('--app_role', 
                                          help='general middleware type of node',
                                          action="store")

        parser_nodesetcreate.add_argument('--app_peaceful', 
                                          help='for workers, job kill policy [True|False]',
                                          action="store",
                                          dest="app_peaceful",
                                          required=False,
                                          default=None 
                                         )

        parser_nodesetcreate.add_argument('--app_lingertime', 
                                          help='for workers, idle suicide time in seconds',
                                          action="store",
                                          dest="app_lingertime",
                                          required=False,
                                          default=None 
                                         )
        
        parser_nodesetcreate.add_argument('--app_killorder', 
                                          help='for workers, kill order policy [newest|oldest]',
                                          action="store",
                                          dest="app_killorder",
                                          required=False,
                                          default=None 
                                         )        
        
        parser_nodesetcreate.add_argument('--nodeinfo', 
                action='store', 
                dest='nodeinfo',
                default = None, 
                help='Invidual node size'
                )

        parser_nodesetcreate.add_argument('--environment', 
                                          help='Environment to be installed per job in the nodeset (e.g. a glidein)',
                                          action="store")

        parser_nodesetcreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_nodesetcreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_nodesetcreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_nodesetcreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     ) 

        parser_nodesetcreate.add_argument('nodesetname', 
            help='name of the nodeset to be created',
            action="store")
      
        parser_nodesetlist = subparsers.add_parser('nodeset-list', 
                                                help='list vc3 nodeset(s)')

        parser_nodesetlist.add_argument('--nodesetname', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified nodeset',
                                         default=None)

        parser_nodesetdelete = subparsers.add_parser('nodeset-delete',
                                                     help='delete a nodeset specification')
        parser_nodesetdelete.add_argument('nodesetname',
                                           action="store")

                                                        
        ########################### Cluster  ##########################################
        parser_clustercreate = subparsers.add_parser('cluster-create', 
                help='create new cluster specification')

        parser_clustercreate.add_argument('clustername', 
                help='name of the cluster to be created',
                action="store")
        
        parser_clustercreate.add_argument('--owner', 
                                         action="store",
                                         required=False, 
                                         help='owner of this cluster template',
                                         default=None)
            
        parser_clustercreate.add_argument('--nodesets', 
                action='store', 
                dest='nodesets',
                default = None, 
                help='comma separated list of nodesets within this cluster'
                )
        
        parser_clustercreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_clustercreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_clustercreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_clustercreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     ) 

        parser_clustercreate.add_argument('--public', 
                                     action="store_true",
                                     dest="public",
                                     help="set visible to all users",
                                     default=False, 
                                     )

        parser_clusterlist = subparsers.add_parser('cluster-list', 
                                                help='list vc3 cluster(s)')

        parser_clusterlist.add_argument('--clustername', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified cluster',
                                         default=None)
    
        parser_clusteraddnodeset = subparsers.add_parser('cluster-addnodeset', 
                help='add a nodeset to a cluster specification')
    
        parser_clusteraddnodeset.add_argument('clustername',
                                              action='store',
                                              help='clustername to add nodeset to'
                                              )

        parser_clusteraddnodeset.add_argument('nodesetname',
                                              action='store',
                                              help='nodeset to add'
                                              )
            
        
        parser_clusterremovenodeset = subparsers.add_parser('cluster-removenodeset', 
                help='add a nodeset to a cluster specification')
    
        parser_clusterremovenodeset.add_argument('clustername',
                                              action='store',
                                              help='clustername to remove nodeset from'
                                              )

        parser_clusterremovenodeset.add_argument('nodesetname',
                                              action='store',
                                              help='nodeset to remove'
                                              )

        parser_clusterdelete = subparsers.add_parser('cluster-delete', 
                help='delete a cluster specification')

        parser_clusterdelete.add_argument('clustername', 
                                          action="store")
            
        
        ########################### Environment  ##########################################
        parser_environcreate = subparsers.add_parser('environment-create', 
                help='create new environment')

        parser_environcreate.add_argument('environmentname', 
                help='name of the environment to be created',
                action="store")

        parser_environcreate.add_argument('--owner',
                action="store", 
                dest="owner", 
                default='unknown')

        parser_environcreate.add_argument('--packages', 
                action='store', 
                dest='packagelist', 
                default=None,
                help='comma separated list of packages to be installed'
                )

        parser_environcreate.add_argument('--envvar', 
                action='append', 
                dest='envmap', 
                default=None,
                help='VAR=VALUE to be set as an environment variable'
                )

        parser_environcreate.add_argument('--filesmap', 
                action='store', 
                dest='filesmap', 
                default=None,
                help='comma separated list of LOCAL=REMOTE file name specifications'
                )

        parser_environcreate.add_argument('--command', 
                action='store', 
                dest='command', 
                default=None,
                help='Command to execute the environment. No two environments in a request may define a command.'
                )

        parser_environcreate.add_argument('--require-os', 
                action='store', 
                dest='required_os', 
                default=None,
                help='Operating System to use. The builder checks for the native OS first and tries container solutions otherwise.'
                )

        parser_environcreate.add_argument('--extra-args', 
                action='append', 
                dest='builder_extra_args', 
                default=None,
                help='Extra argument to pass to the builder.'
                )

        parser_environcreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_environcreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_environcreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_environcreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     ) 
        
        parser_environmentlist = subparsers.add_parser('environment-list', 
                                                help='list vc3 environment(s)')

        parser_environmentlist.add_argument('--environmentname', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified environment',
                                         default=None)

        parser_environdelete = subparsers.add_parser('environment-delete', 
                help='delete an environment')

        parser_environdelete.add_argument('environmentname', 
                help='name of the environment to be deleted',
                action="store")

        
        ########################### Request  ##########################################
        parser_requestcreate = subparsers.add_parser('request-create', 
                help='create new request specification')

        parser_requestcreate.add_argument('requestname', 
                                    help='name of the request to be created',
                                    action="store")

        parser_requestcreate.add_argument('--owner', 
                action='store', 
                dest='owner', 
                help='VC3 User owner of this Request.',
                default=None
                )

        parser_requestcreate.add_argument('--expiration', 
                action='store', 
                dest='expiration', 
                help='Date YYYY-MM-DD,HH:MM:SS at which this request expires',
                default=None
                )

        parser_requestcreate.add_argument('--cluster', 
                action='store', 
                dest='cluster', 
                help='Cluster template to use for this Request.',
                default=None
                )

        parser_requestcreate.add_argument('--policy', 
                action='store', 
                dest='policy', 
                help='Policy for using the allocations',
                default='static-balanced')

        parser_requestcreate.add_argument('--project', 
                action='store', 
                dest='project', 
                help='Project this request is for',
                default=None
                )

        parser_requestcreate.add_argument('--allocations', 
                action='store', 
                dest='allocations', 
                help='Comma-separated list of Allocations to be used by the request',
                default=None
                )

        parser_requestcreate.add_argument('--environments', 
                action='store', 
                dest='environments', 
                help='Comma-separated list of Environments to be used by the request',
                default=None
                )

        parser_requestcreate.add_argument('--description', 
                                     action="store", 
                                     dest="description",
                                     required=False,
                                     default=None 
                                     )

        parser_requestcreate.add_argument('--displayname', 
                                     action="store", 
                                     dest="displayname",
                                     required=False,
                                     default=None 
                                     )        

        parser_requestcreate.add_argument('--url', 
                                     action="store", 
                                     dest="url",
                                     required=False,
                                     default=None 
                                     )         

        parser_requestcreate.add_argument('--docurl', 
                                     action="store", 
                                     dest="docurl",
                                     required=False,
                                     default=None 
                                     ) 

        parser_requestcreate.add_argument('--organization', 
                                     action="store", 
                                     dest="organization",
                                     required=False,
                                     default=None 
                                     )

        parser_requestlist = subparsers.add_parser('request-list', 
                                                help='list vc3 request(s)')

        parser_requestlist.add_argument('--requestname', 
                                         action="store",
                                         required=False, 
                                         help='list details of specified request',
                                         default=None)

        
        parser_requestgetconfstr = subparsers.add_parser('request-getconfstring', 
                                                help='Get configuration string from Request(s)')
        
        parser_requestgetconfstr.add_argument('--requestname', 
                                         action="store",
                                         required=True, 
                                         help='Name of relevant Request.',
                                         default=None)                

        parser_requestgetconfstr.add_argument('--conftype', 
                                         action="store",
                                         required=True, 
                                         help='auth|queues',
                                         default=None) 

        
        parser_requestterminate = subparsers.add_parser('request-terminate', 
                                                help='Terminate request.')
        
        parser_requestterminate.add_argument('--requestname', 
                                         action="store",
                                         required=True, 
                                         help='Name of relevant Request.',
                                         default=None)             

        parser_requeststatus = subparsers.add_parser('request-status', 
                                                help='Get status of the Request.')
        
        parser_requeststatus.add_argument('--requestname', 
                                         action="store",
                                         required=True, 
                                         help='Name of relevant Request.',
                                         default=None)          

        parser_requeststatus.add_argument('--raw', 
                                         action="store_true",
                                         required=False, 
                                         help='Name of relevant Request.',
                                         default=False)  

        parser_requeststate = subparsers.add_parser('request-state', 
                                                help='Get state of the Request.')
        
        parser_requeststate.add_argument('--requestname', 
                                         action="store",
                                         required=True, 
                                         help='Name of relevant Request.',
                                         default=None)          

        parser_requestdelete = subparsers.add_parser('request-delete', 
                help='delete a request specification')

        parser_requestdelete.add_argument('requestname', 
                                    help='name of the request to be deleted',
                                    action="store")

        ########################### Pairing  ##########################################
        parser_pairingcreate = subparsers.add_parser('pairing-create', 
                                                help='create new pairing request')
        
        parser_pairingcreate.add_argument('commonname',
                                           action="store",
                                           help='SSL Subject Common Name (CN); a vc3 username or hostname'            
                                           )

        parser_pairingretrieve = subparsers.add_parser('pairing-retrieve', 
                                                help='Get cert and key for a pairing request')
        
        parser_pairingretrieve.add_argument('pairingcode',
                                           action="store",
                                           help="unique pairing code from original request")       
        
        parser_pairingretrieve.add_argument('--certfile', 
                                     action="store", 
                                     dest="certfile", 
                                     help="path/filename to write SSL certificate",
                                     default=None
                                     ) 
        
        parser_pairingretrieve.add_argument('--keyfile', 
                                     action="store", 
                                     dest="keyfile", 
                                     help="path/filename to write SSL key",
                                     default=None
                                     )        

        self.results= parser.parse_args()


    def setuplogging(self):
        self.log = logging.getLogger()
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        #formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.StreamHandler()
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
    
        self.log.setLevel(logging.WARN)
        if self.results.debug:
            self.log.setLevel(logging.DEBUG)
        if self.results.verbose:
            self.log.setLevel(logging.INFO)
        self.log.info('Logging initialized.')


    def run(self):
        cp = ConfigParser()
        ns = self.results
        self.log.info("Config string is %s" % ns.configpath)
        configpaths = ns.configpath.split(',')
        configfiles = []
        for p in configpaths:
            p = p.strip()
            configfiles.append(os.path.expanduser(p))
        readfiles = cp.read(configfiles)
        self.log.info('Read config files %s' % readfiles)
        capi = VC3ClientAPI(cp)
        
        try:
            # User commands
            if ns.subcommand == 'user-create':
                if ns.sshpubstring and not capi.validate_ssh_pub_key(ns.sshpubstring):
                    self.log.error('ssh pub key is not a valid key.')
                    sys.exit(1)

                u = capi.defineUser( name = ns.username,
                                     first = ns.firstname,
                                     last = ns.lastname,
                                     email = ns.email,
                                     organization = ns.organization,
                                     identity_id = ns.identity_id,
                                     description = ns.description, 
                                     displayname = ns.displayname, 
                                     sshpubstring = ns.sshpubstring, 
                                     url = ns.url, 
                                     docurl = ns.docurl                                  
                                     )
                self.log.debug("User is %s" % u)
                capi.storeUser(u)
                
            elif ns.subcommand == 'user-list' and ns.username is None:
                ulist = capi.listUsers()
                for u in ulist:
                    print(u)
            
            elif ns.subcommand == 'user-list' and ns.username is not None:
                uo = capi.getUser(ns.username)
                print(uo)

            elif ns.subcommand == 'user-delete':
                capi.deleteUser(ns.username)
            
            # Project commands
            elif ns.subcommand == 'project-create':
                if ns.members is not None:
                    memberslist = ns.members.split(',')
                else:
                    memberslist = []
                    
                p = capi.defineProject( name = ns.projectname,
                                        owner = ns.owner,
                                        members = memberslist,
                                        description = ns.description, 
                                        displayname = ns.displayname, 
                                        url = ns.url, 
                                        docurl = ns.docurl,
                                        organization = ns.organization
                                        )
                self.log.debug("Project is %s" % p)
                capi.storeUser(p)    
                
            elif ns.subcommand == 'project-list' and ns.projectname is None:
                plist = capi.listProjects()
                for p in plist:
                    print(p)
            
            elif ns.subcommand == 'project-list' and ns.projectname is not None:
                po = capi.getProject(ns.projectname)
                print(po)
    
            elif ns.subcommand == 'project-adduser':
                capi.addUserToProject(ns.user, ns.projectname)
    
            elif ns.subcommand == 'project-removeuser':
                capi.removeUserFromProject(ns.user, ns.projectname)
            
            elif ns.subcommand == 'project-addallocation':
                capi.addAllocationToProject(ns.allocationname, ns.projectname)
    
            elif ns.subcommand == 'project-removeallocation':
                capi.removeAllocationFromProject(ns.allocationname, ns.projectname)

            elif ns.subcommand == 'project-delete':
                capi.deleteProject(ns.projectname)

                
            # Resource commands
            elif ns.subcommand == 'resource-create':
                r = capi.defineResource( name = ns.resourcename,
                                         owner = ns.owner,
                                         accesstype = ns.accesstype,
                                         accessmethod = ns.accessmethod,
                                         accessflavor = ns.accessflavor,
                                         accesshost = ns.accesshost,
                                         accessport = ns.accessport,
                                         accessgateway = ns.accessgateway,
                                         nodeinfo   = ns.nodeinfo,
                                         scratchdir = ns.scratchdir,
                                         gridresource = ns.gridresource,
                                         cloudspotprice = ns.cloudspotprice,
                                         cloudinstancetype = ns.cloudinstancetype,
                                         mfa = ns.mfa,
                                         public = ns.public,
                                         organization = ns.organization,
                                         description = ns.description, 
                                         displayname = ns.displayname, 
                                         url = ns.url, 
                                         docurl = ns.docurl,
                                         pubtokendocurl = ns.pubtokendocurl
                                          )
                self.log.debug("Resource is %s" % r)
                capi.storeResource(r)    
                
            elif ns.subcommand == 'resource-list' and ns.resourcename is None:
                rlist = capi.listResources()
                for r in rlist:
                    print(r)
            
            elif ns.subcommand == 'resource-list' and ns.resourcename is not None:
                ro = capi.getResource(ns.resourcename)
                print(ro)

            elif ns.subcommand == 'resource-delete':
                capi.deleteResource(ns.resourcename)
            
            
            # Allocation commands
            elif ns.subcommand == 'allocation-create':
                a = capi.defineAllocation( name = ns.allocationname,
                                           owner = ns.owner,
                                           resource = ns.resource,
                                           accountname = ns.accountname,
                                           description = ns.description, 
                                           displayname = ns.displayname, 
                                           url = ns.url, 
                                           docurl = ns.docurl,
                                           pubtokendocurl = ns.pubtokendocurl,
                                           privtoken = ns.privtoken
                                           )
                self.log.debug("Allocation is %s" % a)
                capi.storeAllocation(a)    
                
            elif ns.subcommand == 'allocation-list' and ns.allocationname is None:
                alist = capi.listAllocations()
                for a in alist:
                    print(a)
            
            elif ns.subcommand == 'allocation-list' and ns.allocationname is not None:
                ao = capi.getAllocation(ns.allocationname)
                print(ao)
    
            elif ns.subcommand == 'allocation-getpubtoken':
                pt = capi.getAllocationPubToken(ns.allocationname)
                print(pt)

            elif ns.subcommand == 'allocation-delete':
                capi.deleteAllocation(ns.allocationname)

            elif ns.subcommand == 'allocation-validate':
                ao = capi.getAllocation(ns.allocationname)
                ao.action = 'validate'
                capi.storeAllocation(ao)
    
            # Nodeinfo create, list
            elif ns.subcommand == 'nodeinfo-create':
                n = capi.defineNodeinfo(name = ns.nodeinfoname, 
                                       owner =  ns.owner, 
                                       cores      = ns.cores,
                                       memory_mb  = ns.memory_mb,
                                       storage_mb = ns.storage_mb,
                                       native_os = ns.native_os,
                                       features = [x for x in ns.features.split(',') if x],
                                       description = ns.description, 
                                       displayname = ns.displayname, 
                                       url = ns.url, 
                                       docurl = ns.docurl                                    
                                       )
                capi.storeNodeinfo(n)
    
            elif ns.subcommand == 'nodeinfo-list' and ns.nodeinfoname is None:
                nsl = capi.listNodeinfos()
                for ns in nsl:
                    print(ns)
                    
            elif ns.subcommand == 'nodeinfo-list' and ns.nodeinfoname is not None:
                ns = capi.getNodeinfo(ns.nodeinfoname)
                print(ns)

            elif ns.subcommand == 'nodeinfo-delete':
                capi.deleteNodeinfo(ns.nodeinfoname)

            # Nodeset create, list
            elif ns.subcommand == 'nodeset-create':
                n = capi.defineNodeset(name = ns.nodesetname, 
                                       owner =  ns.owner, 
                                       node_number = ns.node_number, 
                                       app_type = ns.app_type, 
                                       app_role = ns.app_role,
                                       nodeinfo = ns.nodeinfo,
                                       app_peaceful = ns.app_peaceful,
                                       app_lingertime = ns.app_lingertime,
                                       app_killorder = ns.app_killorder,
                                       environment = ns.environment,
                                       description = ns.description, 
                                       displayname = ns.displayname, 
                                       url = ns.url, 
                                       docurl = ns.docurl                                    
                                       )
                capi.storeNodeset(n)
    
            elif ns.subcommand == 'nodeset-list' and ns.nodesetname is None:
                nsl = capi.listNodesets()
                for ns in nsl:
                    print(ns)
                    
            elif ns.subcommand == 'nodeset-list' and ns.nodesetname is not None:
                ns = capi.getNodeset(ns.nodesetname)
                print(ns)

            elif ns.subcommand == 'nodeset-delete':
                capi.deleteNodeset(ns.nodesetname)

                            
            # Cluster template create, list
            elif ns.subcommand == 'cluster-create' and ns.nodesets is not None:
                c = capi.defineCluster( name = ns.clustername,
                                        owner = ns.owner,
                                        nodesets=ns.nodesets.split(','),
                                        public = ns.public,
                                        description = ns.description, 
                                        displayname = ns.displayname, 
                                        url = ns.url, 
                                        docurl = ns.docurl                                     
                                        )
                self.log.debug("Cluster is %s" % c)
                capi.storeCluster(c)    

            elif ns.subcommand == 'cluster-create' and ns.nodesets is None:
                c = capi.defineCluster( name = ns.clustername,
                                        owner = ns.owner,
                                        public = ns.public,
                                        description = ns.description, 
                                        displayname = ns.displayname, 
                                        url = ns.url, 
                                        docurl = ns.docurl
                                        )
                self.log.debug("Cluster is %s" % c)
                capi.storeCluster(c)

            elif ns.subcommand == 'cluster-list' and ns.clustername is None:
                cl = capi.listClusters()
                for co in cl:
                    print(co)
                    
            elif ns.subcommand == 'cluster-list' and ns.clustername is not None:
                co = capi.getCluster(ns.clustername)
                print(co)               
                                            
            elif ns.subcommand == 'cluster-addnodeset':
                capi.addNodesetToCluster( ns.nodesetname,
                                          ns.clustername )
    
            elif ns.subcommand == 'cluster-removenodeset':
                capi.removeNodesetFromCluster(ns.nodesetname,
                                              ns.clustername )

            elif ns.subcommand == 'cluster-delete':
                capi.deleteCluster(ns.clustername)

    
            # Environment commands
            elif ns.subcommand == 'environment-create':
                # defaults
                packs = []
                vars  = {}
                files = {}
    
                if ns.packagelist is not None:
                    packs = ns.packagelist.split(',')
    
                if ns.envmap is not None:
                    for kv in ns.envmap:
                        (key, value) = kv.split('=', 1)
                        vars[key] = value
                
                if ns.filesmap is not None:
                    filemap = ns.filesmap.split(',')
                    for names in filemap:
                        (local, remote) = names.split('=')
                        local = os.path.expanduser(local)
                        self.log.debug("Reading local file %s for remote %s" % (local, remote))
                        with open(local, 'r') as l_f:
                            all = l_f.read()
                            files[remote] = VC3ClientAPI.encode(all)
                
                e = capi.defineEnvironment( name = ns.environmentname,
                                            owner = ns.owner,
                                            packagelist = packs,
                                            envmap      = vars,
                                            files       = files,
                                            command     = ns.command,
                                            required_os = ns.required_os,
                                            builder_extra_args = ns.builder_extra_args,
                                            description = ns.description, 
                                            displayname = ns.displayname, 
                                            url = ns.url, 
                                            docurl = ns.docurl                                        
                                            )
                
                self.log.debug("Environment is %s" % e)
                capi.storeEnvironment(e)
            
            elif ns.subcommand == 'environment-list' and ns.environmentname is None:
                elist = capi.listEnvironments()
                for e in elist:
                    print(e)
            
            elif ns.subcommand == 'environment-list' and ns.environmentname is not None:
                eo = capi.getEnvironment(ns.environmentname)
                print(eo)

            elif ns.subcommand == 'environment-delete':
                capi.deleteEnvironment(ns.environmentname)
                            
            # Request commands
           
            elif ns.subcommand == 'request-create':
                # Handle list args...    
                allocationslist = []
                if ns.allocations is not None:
                    allocationlist = ns.allocations.split(',')
                environmentlist = []
                if ns.environments is not None:
                    environmentlist = ns.environments.split(',')
        
                r = capi.defineRequest( name=ns.requestname,
                                        owner = ns.owner,
                                        cluster=ns.cluster,
                                        allocations=allocationlist,
                                        environments=environmentlist,
                                        policy= ns.policy,
                                        project = ns.project,
                                        expiration=None,
                                        organization = ns.organization,
                                        description = ns.description, 
                                        displayname = ns.displayname, 
                                        url = ns.url, 
                                        docurl = ns.docurl                                    
                                         )
                self.log.debug("Request is %s" % r)
                capi.storeRequest(r)    
            
            elif ns.subcommand == 'request-list' and ns.requestname is None:
                rlist = capi.listRequests()
                for r in rlist:
                    print(r)
            
            elif ns.subcommand == 'request-list' and ns.requestname is not None:
                ro = capi.getRequest(ns.requestname)
                print(ro)
            
            elif ns.subcommand == 'request-getconfstring':
                cs = capi.getConfString(ns.conftype, ns.requestname)
                print(cs)
            
            elif ns.subcommand == 'request-terminate':
                capi.terminateRequest(ns.requestname)
            
            elif ns.subcommand == 'request-status':
                (raw, info) =  capi.getRequestStatus(ns.requestname)
                if ns.raw:
                    print(raw)
                else:
                    print(info)
    
            elif ns.subcommand == 'request-state':
                (state, reason) =  capi.getRequestState(ns.requestname)
                print((str(state), str(reason)))

            elif ns.subcommand == 'request-delete':
                capi.deleteRequest(ns.requestname)

            
            # Pairing commands
            elif ns.subcommand == 'pairing-create':
                code = capi.requestPairing(ns.commonname)
                print(code)        
            
            elif ns.subcommand == 'pairing-retrieve':
                try:
                    (cert, key) = capi.getPairing(ns.pairingcode)
                    if ns.certfile is not None and ns.keyfile is not None:
                        certpath = os.path.expanduser(ns.certfile)
                        keypath = os.path.expanduser(ns.keyfile)
                        cf = open(certpath, 'w')
                        cf.write(cert)
                        cf.close()
                        
                        # Necessary to avoid security issues with world or group writable key file. 
                        if os.path.isfile(keypath):
                            os.remove(keypath)
                        original_umask = os.umask(0o177)  # 0o777 ^ 0o600
                        try:
                            kf = os.fdopen(os.open(keypath, os.O_WRONLY | os.O_CREAT, 0o600), 'w')
                        finally:
                            os.umask(original_umask)
                        kf.write(key)
                        kf.close()                
                        
                    else:
                        # print cert, key to stdout  
                        print(cert)
                        print("")
                        print(key)
                except InfoMissingPairingException:
                    print("Invalid pairing code or not satisfied yet. Try in 30 seconds.")   
            else:
                self.log.warning('Unrecognized subcommand is %s' % ns.subcommand)
                sys.exit(1)
                               
        except InfoEntityUpdateMissingException, e:
            print("Error: Attempt to update/PUT a non-existent entity.")
            sys.exit(2)
        except InfoEntityExistsException, e:
            print("Error: Attempt to create/POST an entity that already exists.")
            sys.exit(2)
        except InfoEntityMissingException, e: 
            print("Error: Attempt to retrieve/GET or delete/DELETE a non-existent entity.")
            sys.exit(3)
        except Exception, e:
            print("Error: Got unexpected exception %s"% e)
            sys.exit(1)
        

if __name__ == '__main__':

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

    vc3cli = VC3ClientCLI()
    try:
        vc3cli.run()
    except Exception:
        print(traceback.format_exc(None))
        sys.exit(1)

