#!/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import logging
import urllib

from vc3infoservice.core import InfoEntity
   
class User(InfoEntity):
    '''
    Represents a VC3 instance user account.
    As policy, name, email, and organization must be set.  
    
    '''
    infoattributes = ['name',
                     'state',
                     'first',
                     'last',
                     'email',
                     'organization',
                     'identity_id',
                     'description',
                     'displayname',
                     'sshpubstring',
                     'url',
                     'docurl'                  
                     ] 
    infokey = 'user'
    validvalues = {}
    intattributes = []
    
    def __init__(self,
                   name,
                   state,
                   first,
                   last,
                   email,
                   organization,
                   identity_id=None,
                   description=None,
                   displayname=None,
                   sshpubstring=None,
                   url=None,
                   docurl=None
                ):
        '''
        Defines a new User object. 
              
        :param str name: The unique VC3 username of this user
        :param str first: User's first name
        :param str last: User's last name
        :param str email: User's email address
        :param str organization: User's institutional affiliation or employer
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.          
        :return: User:  A valid User object      
        :rtype: User
        
        '''
        self.log = logging.getLogger()
        self.state = state
        self.name = name
        self.first = first
        self.last = last
        self.email = email
        self.organization = organization
        self.identity_id = identity_id
        self.allocations = []
        self.description = description
        self.displayname = displayname
        self.sshpubstring = sshpubstring
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)


    def addAllocation(self, allocation):
        '''
            Adds provided allocation (string label) to this allocation.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Adding allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.allocations.append(allocation)
        self.log.debug("Allocations now %s" % self.allocations)
        

    def removeAllocation(self, allocation):
        '''
            Removes provided allocation (string label) to this project.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Removing allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.log.debug("Allocation %s did not belong to project")
        else:
            self.allocations.remove(allocation)
            self.log.debug("Allocations now %s" % self.allocations)


class Project(InfoEntity):
    '''
    Represents a VC3 Project.
    
    '''
    infokey = 'project'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'members', 
                     'allocations',
                     'blueprints',
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     'organization', 
                     ]
    validvalues = {}
    intattributes = []    
    
    def __init__(self, 
                   name,
                   state,
                   owner,
                   members,   # list
                   allocations=[],  # list of names 
                   blueprints=[],
                   description=None,
                   displayname=None,
                   url=None,
                   docurl=None, 
                   organization = None,
                   ):  # list of names
        '''
        Defines a new Project object. 
              
        :param str name: The unique VC3 name of this project
        :param str owner: VC3 username of project owner. 
        :param str members: List of vc3 usernames
        :param str allocations: List of allocation names. 
        :param str blueprints:  List of blueprint names. 
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity. 
        :param str organization: Name of experiment or institution for this project. 
        :return: Project:  A valid Project objext. 
        :rtype: Project
        
        '''  
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner
        self.members = []
        for m in members:
            if m not in self.members:
                self.members.append(m)
        self.allocations = allocations
        self.blueprints = blueprints
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.organization = organization
        self.log.debug("Entity created: %s" % self)
 
    def addUser(self, user):
        '''
            Adds provided user (string label) to this project.
        '''
        if self.members is None:
            self.members = []

        self.log.debug("Adding user %s to project" % user)
        if user not in self.members:
            ulist = self.members
            ulist.append(user)
            self.members = ulist
        self.log.debug("Members now %s" % self.members)
        

    def removeUser(self, user):
        '''
            Removes provided user (string label) from this project.
        '''
        if self.members is None:
            self.members = []

        self.log.debug("Removing user %s to project" % user)
        if user not in self.members:
            self.log.debug("User %s did not belong to project")
        else:
            ulist = self.members
            ulist.remove(user)
            self.members = ulist
            self.log.debug("Members now %s" % self.members)

    def addAllocation(self, allocation):
        '''
            Adds provided allocation (string label) to this project.
        '''
        if self.allocations is None:
            self.allocations = []

        self.log.debug("Adding allocation %s to project" % allocation)
        if allocation not in self.allocations:
            alist = self.allocations
            alist.append(allocation)
            self.allocations = alist
        self.log.debug("Allocations now %s" % self.allocations)
        

    def removeAllocation(self, allocation):
        '''
            Removes provided allocation (string label) from this project.
        '''
        if self.allocations is None:
            self.allocations = []

        self.log.debug("Removing allocation %s from project" % allocation)
        if allocation not in self.allocations:
            self.log.debug("Allocation %s did not belong to project")
        else:
            alist = self.allocations
            alist.remove(allocation)
            self.allocations = alist
            self.log.debug("Allocations now %s" % self.allocations)

class Resource(InfoEntity):
    '''
    Represents a VC3 target resource. 
    
    Intrinsic time limits/preemption flag to distinguish platforms we could run static components on. 
    Network access is also critical for this.    
        
    '''
    infokey = 'resource'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'accesstype', 
                     'accessmethod',
                     'accessflavor',
                     'accesshost',
                     'accessport',
                     'accessgateway', 
                     'nodeinfo',
                     'scratchdir',
                     'gridresource',
                     'cloudspotprice',
                     'cloudinstancetype',
                     'mfa',
                     'public',
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     'pubtokendocurl',
                     'organization',
                     ]
    validvalues = {
        'accesstype' : ['batch','cloud']
        }
    intattributes = []
    
    def __init__(self,
                 name,
                 state,
                 owner,
                 accesstype,   # grid, batch, cloud
                 accessmethod, # ssh, gsissh
                 accessflavor, # condor-ce, slurm, sge, ec2, nova, gce
                 accesshost,   # hostname
                 accessport,   # port
                 gridresource, # http://cldext02.usatlas.bnl.gov:8773/services/Cloud , HTCondor CE hostname[:port]              
                 nodeinfo,     # name of the Nodeinfo describing the size of the nodes in this resource
                 scratchdir='/home/${USER}', # root dir for vc3-resource-manager to installs stuff.
                 accessgateway = None, # if site has, e.g. SSH gateway which must be traversed.
                 cloudspotprice = None,
                 cloudinstancetype = None,
                 mfa = False,
                 public = False, # should this resource be shown to all users? Default: No.
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None,
                 pubtokendocurl=None, # special instructions for ssh public keys.
                 organization = None,
                 ):
        '''
    Creates a new Resource object.
        
    :param str description: Long-form description
    :param str displayname: Pretty human-readable name/short description
    :param str url: High-level URL reference for this entity. 
    :param str docurl: Link to how-to/usage documentation for this entity.     
        '''
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner
        
        # Entity-specific attriutes
        self.accesstype = accesstype
        self.accessmethod = accessmethod
        self.accessflavor = accessflavor
        self.accesshost = accesshost
        self.accessport = accessport
        self.nodeinfo = nodeinfo
        self.scratchdir = scratchdir
        self.accessgateway = accessgateway
        self.gridresource = gridresource
        self.cloudspotprice    = cloudspotprice
        self.cloudinstancetype = cloudinstancetype
        self.mfa = mfa
        self.public = public
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.pubtokendocurl = pubtokendocurl
        self.organization = organization

        self.log.debug("Entity created: %s" % self)


class Allocation(InfoEntity):
    '''
    Represents the access granted a VC3 User and a VC3 target Resource.
    Defined by (resource, vc3user, unix_account) triple.   
    
    May or may not contain sub-Allocations.
    
    (Top-level) Allocation names are in the form <vc3username>.<vc3resourcename>.
    Sub-allocation names are in the form <vc3username>.<vc3resourcename>.<suballocationlabel>
            
    '''
    infokey = 'allocation'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'resource',
                     'type',        # unlimited, quota, cumulative
                     'accountname',
                     'action',
                     'state_reason',
                     'quantity',
                     'units',       # corehours, su, nodes, 
                     'sectype',     # ssh-rsa, ssh-dsa, pki, x509, local
                     'pubtoken',    # ssh pubkey, cloud access key
                     'privtoken',   # ssh privkey, cloud secret key, VOMS proxy
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     'pubtokendocurl',
                    ]
    validvalues = {
        'sectype' : [ None, 'ssh-rsa', 'ssh-dsa' , 'x509' ],
        }
    intattributes = []    
    
    def __init__(self, 
                 name, 
                 state, 
                 owner,
                 resource, 
                 accountname,
                 action='new',
                 state_reason=None,
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None,
                 pubtokendocurl=None,
                 type='unlimited', 
                 quantity=None, 
                 units=None,
                 sectype=None,
                 pubtoken=None,
                 privtoken=None, 
                  ):
        '''
    Creates a new Allocation object. 
            
    :param str description: Long-form description
    :param str displayname: Pretty human-readable name/short description
    :param str url: High-level URL reference for this entity. 
    :param str docurl: Link to how-to/usage documentation for this entity. 
        
        '''
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner
        self.resource = resource
        self.accountname = accountname     # unix username, or cloud tenant, 
        self.action = action               # None | new | validate
        self.state_reason = state_reason
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.pubtokendocurl = pubtokendocurl
        self.type = type           # quota | unlimited | limited 
        self.quantity = quantity   # 
        self.units = units         #
        self.sectype = sectype
        self.pubtoken = pubtoken
        self.privtoken = privtoken
        self.log.debug("Entity created: %s" % self)

class Policy(InfoEntity):
    '''
    Describes the desired resource utilization policy when a Request 
    includes multiple Allocations. 

    '''
    infokey = 'policy'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'pluginname',
                     'description',
                     'displayname',
                     'url',
                     'docurl', 
                      ]
    validvalues = {}
    intattributes = []
    
    
    def __init__(self, 
                 name, 
                 state, 
                 owner, 
                 pluginname,
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None,  ):
        '''
        Creates a new Policy object. 
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.             
        
        '''
        self.log = logging.getLogger()
        self.name = name
        self.owner = owner
        self.pluginname = pluginname
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)


class Nodeinfo(InfoEntity):
    '''
    Represents the computational resources of a node in a homogenous Nodeset

    '''
    infokey = 'nodes'
    infoattributes = ['name',
                     'state',
                     'owner',
                     
                     'cores',             # per node
                     'memory_mb',         # per node
                     'storage_mb',        # per node

                     'native_os',
                     'features',

                     'description',
                     'displayname',
                     'url',
                     'docurl', 
                     ]
    intattributes = [ 'cores',
                      'memory_mb',
                      'storage_mb'
                     ]
    
    def __init__(self, name, 
                       state,
                       owner, 
                       cores,
                       memory_mb,
                       storage_mb,
                       native_os,
                       features = [],     # list of strings of fetaures this resource has (e.g. 'singularity', and 'cvmfs')
                       description=None,
                       displayname=None,
                       url=None,
                       docurl=None,  
                       ):
        '''
        Creates a new Nodeinfo object. 
        
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.  
        :param str environment:  Environment to preload per job (e.g. a glidein)
            
        '''
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner
        
        self.cores = cores
        self.memory_mb = memory_mb
        self.storage_mb = storage_mb
        self.native_os = native_os
        self.features = features

        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)

class Nodeset(InfoEntity):
    '''
    Represents a set of equivalently provisioned nodes that are part of a Cluster definition. 

    '''
    infokey = 'nodes'
    infoattributes = ['name',
                     'state',
                     'state_reason',
                     'owner',
                     
                     'node_number',
                     'app_type',
                     'app_role',

                     'nodeinfo',
                     
                     'app_host',
                     'app_port',
                     'app_sectoken',
                     'app_peaceful',
                     'app_lingertime',
                     'app_killorder',            
                     'environment',
                     'description',
                     'displayname',
                     'url',
                     'docurl', 
                     ]
    validvalues = {
        'app_type' : ['htcondor' , 'workqueue', 'spark', 'jupyter+htcondor', 'jupyter+spark', 'reana+htcondor', 'generic' ],
        'app_role' : ['head-node' , 'worker-nodes' ],
        'app_killorder' : ['newest' , 'oldest'],
        }
    intattributes = [ 'node_number', 'app_lingertime' ]
    nameattributes = ['owner','displayname']
    
    def __init__(self, name, 
                       state,
                       owner, 
                       node_number, 
                       app_type, 
                       app_role,
                       resource_type='allocation',   # external, managed, allocation, resource-info
                       state_reason=None,
                       nodeinfo=None,
                       app_host = None, 
                       app_port = None,
                       app_sectoken = None,
                       app_peaceful = True,  
                       app_lingertime = None, 
                       app_killorder = None,
                       environment = None,
                       description=None,
                       displayname=None,
                       url=None,
                       docurl=None,  
                       ):
        '''
        Creates a new Nodeset object. 
        
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.  
        :param str environment:  Environment to preload per job (e.g. a glidein)
            
        '''
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.state_reason = state_reason
        self.owner = owner
        self.node_number = node_number
        self.app_type = app_type
        self.app_role = app_role
        self.resource_type = resource_type
        
        self.nodeinfo = nodeinfo

        self.app_host = app_host
        self.app_port = app_port
        self.app_sectoken = app_sectoken
        self.app_peaceful = app_peaceful  
        self.app_lingertime = app_lingertime
        self.app_killorder = app_killorder 
        self.environment = environment
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)

   
      
        
class Cluster(InfoEntity):
    '''
    AKA a Cluster Template
    
    Represents a supported VC3 middleware cluster application, node layout, and all relevant 
    configuration and dependencies to instantiate it. It is focussed on building the virtual 
    *cluster* not the task/job Environment needed to run a particular user's domain application. 
    
    Cluster descriptions should be generic and shareable across Users/Projects. 
    
    '''
    infokey = 'cluster'
    infoattributes = [ 'name',
                        'state',
                        'owner',
                        'nodesets',
                        'public',
                        'description',
                        'displayname',
                        'url',
                        'docurl',
                      ]
    validvalues = {}
    intattributes = []
    nameattributes = ['owner','displayname']

    def __init__(self, 
                 name, 
                 state, 
                 owner, 
                 nodesets,
                 public=False,
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None ):
        '''
        Creates a new Cluster object. 
        
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.  
        '''
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner
        self.nodesets = nodesets # ordered list of nodeset labels
        self.public = public
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)

    def addNodeset(self, nodesetname ):
        if self.nodesets is None:
            self.nodesets = []

        if nodesetname not in self.nodesets:
            nlist = self.nodesets
            nlist.append(nodesetname)
            self.nodesets = nlist


    def removeNodeset(self, nodesetname):
        if self.nodesets is None:
            self.nodesets = []


        if nodesetname not in self.nodesets:
            self.log.debug("Nodeset %s did not belong to Cluster" % nodesetname)
        else:
            nlist = self.nodesets
            nlist.remove(nodesetname)
            self.nodesets = nlist

        if nodesetname in self.nodesets:
            self.nodesets.remove(nodesetname)
                    

class Environment(InfoEntity):
    '''
    Represents the node/job-level environment needed to run a given user task. 
    Consists of task requirements like job runtime, disk space, cpucount, gpu
    Consists of job requirements like application software, network access, http cache, CVMFS, etc. 
    
    '''
    infokey = 'environment'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'packagelist',
                     'envmap',
                     'files',
                     'command',
                     'required_os',
                     'builder_extra_args',
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     ]
    validvalues = { }
    intattributes = []

    def __init__(self, 
                 name, 
                 state, 
                 owner, 
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None,  
                 packagelist=[], 
                 envmap={}, 
                 files={}, 
                 command = None,
                 required_os = None,
                 builder_extra_args = None):
        '''
        Defines a new Environment object. 
                  
        :param str name: The unique VC3 label for this environment.
        :param str owner:
        :param List str packagelist:
        :param Dict str->str envmap: 
        :param Dict str->str files: remote-name->contents files. Files to be included in the environment. (Files will be base64 encoded.)
        :param str command: command to execute the environment inside the builder. (e.g., vc3-glidein -c ...)
        :param str required_os: operating system to use inside the builder (natively or via container solutions, as needed)
        :param List builder_extra_args: extra arguments to pass to the builder.
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity. 
        :rtype: Environment
        
        '''  
        self.log = logging.getLogger()
        self.name  = name
        self.state = state
        self.owner = owner
        self.packagelist = packagelist
        self.envmap = envmap
        self.files = files
        self.command = command
        self.required_os = required_os
        self.builder_extra_args = builder_extra_args
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)


class Request(InfoEntity):
    '''
    Represents and contains all information relevant to a concrete virtual cluster. 
    Contains sub-elements that reflect information from other Entities. 
    expiration:  Date or None   Time at which cluster should unconditionally do teardown if 
                                not actively terminated. 
    '''
    infokey = 'request'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'action',        # Command from webportal (run, terminate, etc.)
                     'state_reason',
                     'expiration',
                     'project',       # project this request is on behalf of 
                     'queuesconf',    # base64-encoded contents of factory queues.conf sections. 
                     'authconf',      # base64-encoded contents of factory auth.conf sections. 
                     'headnode',      # ip for the headnode associated with this request
                     'policy',        # name of policy to use to satisfy request
                     'allocations',   # list of allocations to satisfy this request
                     'environments',  # list of environments to satisfy this request
                     'cluster',       # contains cluster def, which includes nodeset descriptions
                     'statusraw',     # raw dictionary of submissions for all factories+allocations.
                     'statusinfo',    # aggregated submission status
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     'organization',                     
                     ]
    validvalues = {
                    'state' : ['new', 
                              'initializing',
                              'pending', 
                              'running', 
                              'terminating', 
                              'cleanup', 
                              'terminated',
                              'failure'],
                     'action' : [ 'new', 'run', 'terminate' ]
                    } 
    intattributes = []
    
    def __init__(self, 
                 name, 
                 state, 
                 owner,
                 action = None,    # run | terminate
                 state_reason = None,
                 expiration = None,
                 project = None,
                 queuesconf = None,
                 authconf = None, 
                 headnode = None,
                 cluster =None, 
                 policy = None, 
                 allocations  = [],
                 environments = [],
                 statusraw = None,
                 statusinfo = None,
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None,
                 organization = None,  
                 ):
        '''
        Creates a new Request object. 
        
        :param str name:          Label for this request. 
        :param str state:         State of request
        :param str state_reason:  Error reporting for state
        :param str project:       Name of project the Request is on behalf of
        :param str action:        Command from webportal (e.g. run, terminate, etc.)
        :param str allocations:   List of allocations that the request shoud utilize.
        :param str policy:        Policy for utilizing the allocations. 
        :param str expiration:    Date YYYY-MM-DDTHH:MM:SS when this cluster expires and should be unconditionally terminated. (UTC)
                
        '''
        # Common attributes
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.owner = owner


        # Request-specific attributes
        self.action = action
        self.state_reason = state_reason
        self.expiration  = expiration
        self.project = project
        self.queuesconf = queuesconf
        self.authconf = authconf
        self.statusraw = statusraw
        self.statusinfo = statusinfo
        self.headnode = headnode
        
        # Composite attributes from other entities. 
        self.cluster = cluster
        self.policy  = policy

        if allocations is None:
            allocations = []
        if environments is None:
            environments = []

        self.allocations  = allocations
        self.environments = environments
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.organization = organization
        self.log.debug("Entity created: %s" % self)


class Provisioner(InfoEntity):
    '''
    Represents a VC3 provisioner component (e.g. vc3-factory, kubernetes?, other?)
        
    '''
    infokey = 'provisioner'
    infoattributes = ['name',
                     'state',
                     'owner',
                     'type', # autopyfactory, kubernetes
                     'authconfig',
                     'queuesconf',
                     'description',
                     'displayname',
                     'url',
                     'docurl', 
                     ]
    validvalues = {}
    intattributes = []

    def __init__(self, 
                 name, 
                 state, 
                 provtype='autopyfactory', 
                 authconfig=None, 
                 queuesconfig=None,
                 description=None,
                 displayname=None,
                 url=None,
                 docurl=None, 
                  ):
        '''
        Creates a new Provisioner object. 
              
        :param str name: The unique object name.
        :param str owner:
        :param str type:  What sort of provisioner [autopy/vc3-factory]
        :param str authconfig: (base64encoded) contents of auth.conf for a vc3-factory   
        :param str queuesconfig:  (base64encoded) contents of auth.conf a vc3-factory
        :rtype: Provisioner
        :return: Valid Provisioner object.  
        '''  
        self.log = logging.getLogger()
        self.name  = name  # i.e. factory-id
        self.state = state
        self.owner = owner
        self.type = provtype
        self.authconfig = authconfig
        self.queuesconfig = queuesconfig
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)

class PrivateToken(InfoEntity):
    '''
    Holder for private security tokens, so that read access can be controlled at
    a fine-grained level.

    '''
    infokey = 'privatetoken'
    infoattributes = ['name',
                     'state',
                     'data', # String representation of the token
                     'type', # cloud private key, ssh private key, proxy?
                     'displayname',
                     'url',
                     'docurl',
                     ]
    validvalues = {}
    intattributes = []

    def __init__(self,
                 name,
                 state,
                 data,
                 type,
                 displayname=None,
                 url=None,
                 docurl=None,
                  ):
        '''
        Creates a new PrivateToken object.

        :param str name: The unique object name.
        :param str state: State of token (new|validated)
        :param str type:  What sort of token?
        :rtype: PrivateToken
        :return: Valid PrivateToken object.
        '''
        self.log = logging.getLogger()
        self.name  = name  # i.e. factory-id
        self.state = state
        self.data = data
        self.type = type
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)

        
if __name__ == '__main__':
    pass
    

