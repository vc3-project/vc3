#!/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import ast
import base64
import json
import logging
import os
import sys
import subprocess
import tempfile
import yaml
import StringIO
import ConfigParser

from entities import User, Project, Resource, Allocation, Nodeinfo, Nodeset, Request, Cluster, Environment
from vc3infoservice import infoclient
from vc3infoservice.core import  InfoMissingPairingException, InfoConnectionFailure, InfoEntityExistsException, InfoEntityMissingException, InfoEntityUpdateMissingException


class PermissionDenied(Exception):
    """
    Exception thrown by code when user doesn't have the
    proper permissions for an operation
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class VC3ClientAPI(object):
    '''
    Client application programming interface. 
    
    -- DefineX() methods return object. CreateX() stores it to infoservice. The two steps will allow 
    some manipulation of the object by the client, or calling user. 
    
    -- Oriented toward exposing only valid operations to external
    user (portal, resource tool, or admin CLI client). 
    
    -- Direct manipulations of stored information in the infoservice is only done by Entity objects, not
    client user.
        
    -- Store method (inside of storeX methods) takes infoclient arg in order to allow multiple infoservice instances in the future. 
        
    '''
    
    def __init__(self, config):
        self.config = config
        self.ic = infoclient.InfoClient(self.config)
        self.log = logging.getLogger('vc3client')

    ################################################################################
    #                           Policy related checks
    ################################################################################

    def __has_validated_allocation(self, user=None):
        """
        Check to see if the
        :param user: name from User object (e.g. User.name)
        :return: True if user has a validated allocation
        """
        allocations = self.listAllocations()
        for allocation in allocations:
            if user == allocation.owner and allocation.state == "validated":
                return True
        return False

    def __has_project(self, user=None):
        """
        Checks to see if user owns a project or is a member of an existing project

        :param user: name from User object (e.g. User.name)
        :return: True if user is owns a project or is a project member
        """
        projects = self.listProjects()
        for project in projects:
            if user == project.owner or user in project.members:
                return True
        return False

    def __valid_user(self, user=None):
        """
        Checks to see if user is in the info system

        :param user: name from User object (e.g. User.name)
        :return: True if user is in the info system, False otherwise
        """
        try:
            user_obj = self.getUser(user)
            if user_obj is None:
                return False
        except InfoEntityMissingException:
            return False
        return True

    ################################################################################
    #                           User-related calls
    ################################################################################
    def defineUser(self,
                   name,
                   first,
                   last,
                   email,
                   organization,
                   identity_id = None,
                   description = None,
                   displayname = None,
                   sshpubstring = None,
                   url = None,
                   docurl = None,
                   ):           
        '''
       Defines a new User object for usage elsewhere in the API. 
              
       :param str name: The unique VC3 username of this user
       :param str first: User's first name
       :param str last: User's last name
       :param str email: User's email address
       :param str organization: User's institutional affiliation or employer
       :return: User  A valid User object
       
       :rtype: User        
        '''
        u = User( name=name, 
                  state='new', 
                  first=first, 
                  last=last, 
                  email=email, 
                  organization = organization,
                  identity_id  = identity_id,
                  description  = description,
                  displayname  = displayname,
                  sshpubstring = sshpubstring,
                  url = url,
                  docurl = docurl
                  )
        u.storenew = True
        self.log.debug("Creating user object: %s " % u)
        return u
    
        
    def storeUser(self, user):
        '''
        Stores the provided user in the infoservice. 
        :param User u:  User to add. 
        :return: None
        '''
        user.store(self.ic)
          

    def listUsers(self):
        '''
        Returns list of all valid users as a list of User objects. 

        :return: return description
        :rtype: List of User objects. 
        
        '''
        return self.ic.listentities(User)
       
    def getUser(self, username):
        return self.ic.getentity(User , username)
    
    def deleteUser(self, username):
        self.ic.deleteentity( User, username)
    
    ################################################################################
    #                           Project-related calls
    ################################################################################  
    def defineProject(self, 
                      name, 
                      owner, 
                      members,
                      description = None,
                      displayname = None,
                      url = None,
                      docurl = None,
                      organization = None,                      
                      policy_user=None):
        '''
        Defines a new Project object for usage elsewhere in the API. 
              
        :param str name: The unique VC3 name of this project
        :param str owner:  The VC3 user name of the owner of this project
        :param List str:  List of VC3 user names of members of this project.
        :param str policy_user: The VC3 user name of the user trying this operation
        :return: Project  A valid Project object
        :rtype: Project        
        '''
        if policy_user is not None and not self.__has_validated_allocation(owner):
            raise PermissionDenied("{0} doesn't have a validated allocation".format(policy_user))
        p = Project( name=name,
                     state='new', 
                     owner=owner, 
                     members=members,
                     allocations=[],
                     blueprints=[],
                     description = description,
                     displayname = displayname,
                     url = url,
                     docurl = docurl,
                     organization = organization                     
                     )

        p.addUser(owner)

        p.storenew = True
        self.log.debug("Created project object: %s " % p)
        return p

    def storeProject(self, project, policy_user=None):
        '''
        Stores the provided project in the infoservice. 
        
        :param Project project:  Project to add. 
        :param str policy_user: The VC3 user name of the user trying this operation
        :return: None
        '''
        self.log.debug("Storing project %s" % project)
        if policy_user is not None and policy_user != project.owner:
            raise PermissionDenied("{0} is not the project owner".format(policy_user))
        project.store(self.ic)
        self.log.debug("Done.")
    
    def addUserToProject(self, user, project, policy_user=None):
        '''
        :param str project
        :param str user
        :param str policy_user: The VC3 user name of the user trying this operation
        '''
        self.log.debug("Looking up user %s project %s " % (user, project))
        po = self.getProject(project)
        if po is None:
            self.log.warning("Could not find project object %s " % (po,))
        else:
            if policy_user is not None and po.owner != policy_user:
                raise PermissionDenied("{0} is not the project owner".format(policy_user))
            self.log.debug("Adding user %s to project object %s " % (user, po))
            po.addUser(user)
            self.storeProject(po)        

    def removeUserFromProject(self, user, project, policy_user=None):
        '''
        :param str project
        :param str user
        :param str policy_user: The VC3 user name of the user trying this operation
        '''
        self.log.debug("Looking up user %s project %s " % (user, project))
        po = self.getProject(project)
        if po is None:
            self.log.warning("Could not find project object %s " % (po,))
        else:
            self.log.debug("Removing user %s from project object %s " % (user, po))
            if policy_user is not None:
                if po.owner != policy_user and user not in po.members:
                    err_msg = "{0} is not allowed ".format(policy_user)
                    err_msg += "to remove {0} from {1}".format(user.displayname,
                                                               project)
                    raise PermissionDenied(err_msg)

            po.removeUser(user)
            self.storeProject(po)
        self.log.debug("Removing user %s from project object %s " % (user, po))
        po.removeUser(user)
        self.storeProject(po)

    def addAllocationToProject(self, allocation, projectname, policy_user=None):
        '''
        :param str projectname:
        :param str allocation:
        :param str policy_user: The VC3 user name of the user trying this operation
        '''
        self.log.debug("Looking up allocation %s project %s " % (allocation, projectname))
        if policy_user is not None:
            alloc = self.getAllocation(allocation)
            if policy_user != alloc.owner:
                raise PermissionDenied(policy_user +
                                       "does not own this allocation")
        po = self.getProject(projectname)
        if po is None:
            self.log.warning("Could not find project object %s " % (po,))
        else:
            self.log.debug("Adding allocation %s to project object %s " % (allocation, po))
            po.addAllocation(allocation)
            self.storeProject(po)
        
    def removeAllocationFromProject(self, allocation, projectname, policy_user=None):
        '''
        :param str project
        :param str allocation
        :param str policy_user: The VC3 user name of the user trying this operation
        '''
        self.log.debug("Looking up allocation %s project %s " % (allocation, projectname))
        if policy_user is not None:
            alloc = self.getAllocation(allocation)
            if policy_user != alloc.owner:
                raise PermissionDenied(policy_user +
                                       "does not own this allocation")

        po = self.getProject(projectname)
        if po is None:
            self.log.warning("Could not find project object %s " % (po,))
        else:
            self.log.debug("Removing allocation %s from project object %s " % (allocation, po))
            po.removeAllocation(allocation)
            self.storeProject(po)

    def listProjects(self, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None and not self.__valid_user(policy_user):
            raise PermissionDenied(policy_user + "is not a valid user")
        return self.ic.listentities(Project)
       
    def getProject(self, projectname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None and not self.__valid_user(policy_user):
            raise PermissionDenied(policy_user + "is not a valid user")
        return self.ic.getentity(Project, projectname)

    def getProjectsOfOwner(self, ownername, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None and not self.__valid_user(policy_user):
            raise PermissionDenied(policy_user + "is not a valid user")
        projects = self.listProjects()
        filtered = [ p for p in projects if ownername == p.owner ]
        return filtered

    def getProjectsOfUser(self, username, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None and not self.__valid_user(policy_user):
            raise PermissionDenied(policy_user + "is not a valid user")
        projects = self.listProjects()
        filtered = [ p for p in projects if username in p.members ]
        return filtered

    def deleteProject(self, projectname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            po = self.getProject(projectname)
            if po is not None and po.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the project owner")
        self.ic.deleteentity( Project, projectname)

        
    ################################################################################
    #                           Resource-related calls
    ################################################################################    
    def defineResource(self, 
                       name,
                       owner, 
                       accesstype, 
                       accessmethod, 
                       accessflavor,
                       accesshost, 
                       accessport,  
                       nodeinfo,
                       scratchdir,
                       gridresource, 
                       cloudspotprice,
                       cloudinstancetype,
                       mfa,
                       accessgateway = None,
                       public = False,
                       description = None,
                       displayname = None,
                       url = None,
                       docurl = None,
                       pubtokendocurl = None,
                       organization = None,
                       ):
        '''
        Defines a new Resource object for usage elsewhere in the API. 
              
        :param str name: The unique VC3 name of this resource
        :param str owner:  The VC3 user name of the owner of this project
        :param str resourcetype,  # grid remote-batch local-batch cloud
        :param str accessmethod,  # ssh, gsissh,  
        :param str accessflavor,  # htcondor-ce, slurm, sge, ec2, nova, gce
        :param str accesshost,    # DNS hostname
        :param str accessport,    # 22 , 6918, 8773
        :param str accessgateway, # if relevant, gateway to hop through to get to back end. 
        :param gridresource,      # http://cldext02.usatlas.bnl.gov:8773/services/Cloud  | HTCondorCE hostname             
        :param Boolean mfa        # Does site need head-node factory?     
        :param Boolean public     # Should it be shown to all users?
        :param str pubtokendocurl # # Used when special intructions for using ssh public keys exist
        :return: Resource          A valid Project object
        :rtype: Resource        
        
        '''
        r = Resource( name, 
                      state='new', 
                      owner=owner, 
                      accesstype=accesstype, 
                      accessmethod=accessmethod, 
                      accessflavor=accessflavor, 
                      accesshost = accesshost,
                      accessport = accessport,
                      accessgateway = accessgateway,
                      nodeinfo   = nodeinfo,
                      scratchdir = scratchdir,
                      gridresource=gridresource, 
                      mfa=mfa,
                      public = public,
                      description = description,
                      displayname = displayname,
                      url = url,
                      docurl = docurl,
                      pubtokendocurl = pubtokendocurl,
                      organization = organization                      
                       )
        r.storenew = True
        self.log.debug("Creating Resource object: %s " % r)
        return r
    
    
    def storeResource(self, resource):
        resource.store(self.ic)
    
    def listResources(self):
        return self.ic.listentities(Resource)
       
    def getResource(self, resourcename):
        return self.ic.getentity(Resource, resourcename)

    def deleteResource(self, resourcename):
        self.ic.deleteentity( Resource, resourcename)


    ################################################################################
    #                           Allocation-related calls
    ################################################################################ 
    def defineAllocation(self, name,
                               owner, 
                               resource, 
                               accountname,
                               description=None,
                               displayname=None,
                               url=None,
                               docurl=None,  
                               pubtokendocurl=None,
                               privtoken=None,
                               ):
        '''
          
        '''

        ao = Allocation(name, 
                        state='new', 
                        owner=owner, 
                        resource=resource, 
                        accountname=accountname,
                        description=description,
                        displayname=displayname,
                        url=url,
                        docurl=docurl,
                        pubtokendocurl=pubtokendocurl,
                        privtoken=privtoken,
                        )
        ao.storenew = True
        self.log.debug("Creating Allocation object: %s " % ao)
        return ao

    def storeAllocation(self, allocation, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            if not self.__valid_user(policy_user):
                raise PermissionDenied(policy_user + "is not a valid user")

            # verify allocation is referencing a valid resource
            try:
                resource = self.getResource(allocation.resource)
                if resource is None:
                    raise PermissionDenied(policy_user + "is not a valid resource")
            except InfoEntityMissingException:
                raise PermissionDenied(policy_user + "is not a valid resource")

            # verify only displayname or description is being changed
            try:
                tmp = self.getAllocation(allocation.name)
                if (tmp.owner != allocation.owner or
                    tmp.resource != allocation.resource or
                    tmp.accountname != allocation.accountname or
                    tmp.url != allocation.url):
                    raise PermissionDenied("Trying to modify protected " +
                                           "allocation attributes")
            except InfoEntityMissingException:
                # if allocation isn't in infoservice, check not needed
                pass
        allocation.store(self.ic)

    def listAllocations(self):
        return self.ic.listentities( Allocation )
       
    def getAllocation(self, allocationname):
        return self.ic.getentity( Allocation, allocationname)

    def deleteAllocation(self, allocationname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            alloc = self.getAllocation(allocationname)
            if alloc is not None and alloc.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the allocation owner")
        self.ic.deleteentity( Allocation, allocationname)


    def getAllocationPubToken(self, allocationname):
        alloc = self.getAllocation(allocationname)
        if alloc is None:
            self.log.warning('Could not find allocation object %s' % allocationname)
        else:
            if alloc.pubtoken is not None:
                try:
                    pubstring  = self.decode(alloc.pubtoken)
                    return pubstring
                except Exception, e:
                    self.log.error('Error decoding pubtoken for Allocation %s' % allocationname)                

            
    ################################################################################
    #                        Cluster-related calls
    ################################################################################ 
        '''
        Defines a new Cluster (description) object for usage elsewhere in the API. 
              
        :param str name: The unique name of this cluster description.
        :param str owner:  The user name of the owner of this project
        :param [str]:   List of strings, names of nodesets in this cluster    
        :param Boolean public     Should it be shown to all users?
        :return: Cluster          A valid Cluster object
        :rtype: Cluster        
        
        '''
    def defineCluster(self, 
                      name, 
                      owner, 
                      nodesets=[],
                      public=False,
                      description = None,
                      displayname = None,
                      url = None,
                      docurl = None,                       
                       ): 
        
        c = Cluster(name=name, 
                    state='new',
                    owner=owner,
                    nodesets=nodesets, # list of names of nodesets in this cluster definition.
                    public=public,     # visible to all users?
                    description = description,
                    displayname = displayname,
                    url = url,
                    docurl = docurl 
                     )
        c.storenew = True
        return c
                    
    def storeCluster(self, cluster, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            if cluster.owner != policy_user:
                raise PermissionDenied(policy_user +
                                       "is not owner of entity")

            if not self.__valid_user(policy_user):
                raise PermissionDenied(policy_user +
                                       "is not a valid user")

            if (self.__has_validated_allocation(policy_user) or
                    self.__has_project(policy_user)):
                pass
            else:
                # user needs a validated allocation or to be a project member to
                # store a template
                raise PermissionDenied(policy_user +
                                       "needs a valid allocation or " +
                                       "be a project member")
        cluster.store(self.ic)
    
    def listClusters(self, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            if not self.__valid_user(policy_user):
                raise PermissionDenied(policy_user +
                                       "is not a valid user")

            if (self.__has_validated_allocation(policy_user) or
                    self.__has_project(policy_user)):
                pass
            else:
                # user needs a validated allocation or to be a project member to
                # store a template
                raise PermissionDenied(policy_user +
                                       "needs a valid allocation or " +
                                       "be a project member")
        return self.ic.listentities(Cluster)
       
    def getCluster(self, clustername):
        return self.ic.getentity(Cluster, clustername)

    def deleteCluster(self, clustername, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            cluster = self.getCluster(clustername)
            if cluster is not None and cluster.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the cluster owner")
        self.ic.deleteentity(Cluster , clustername)

    def addNodesetToCluster(self, nodesetname, clustername, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            cluster = self.getCluster(clustername)
            if cluster is not None and cluster.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the cluster owner")

        co = self.getCluster(clustername)
        if co is None:
            self.log.warning('Could not find cluster object %s', clustername)
        else:
            co.addNodeset(nodesetname)
            self.storeCluster(co, policy_user)
       
    def removeNodesetFromCluster(self, nodesetname, clustername, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            cluster = self.getCluster(clustername)
            if cluster is not None and cluster.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the cluster owner")

        co = self.getCluster(clustername)
        if co is None:
            self.log.warning('Could not find cluster object %s', clustername)
        else:
            co.removeNodeset(nodesetname)
            self.storeCluster(co, policy_user)

    ################################################################################
    #                        NodeDescription-related calls
    ################################################################################ 
    def defineNodeinfo(self,
                      name,
                      owner,
                      cores      = 1,
                      memory_mb  = 1024,
                      storage_mb = 1024,
                      native_os  = 'unknown',
                      features = [],
                      description = None,
                      displayname = None,
                      url = None,
                      docurl = None,
                      ):

        ns = Nodeinfo(name=name,
                      state='new',
                      owner=owner,
                      cores      = cores,
                      memory_mb  = memory_mb,
                      storage_mb = storage_mb,
                      native_os = native_os,
                      features  = features,
                      description = description,
                      displayname = displayname,
                      url = url,
                      docurl = docurl
                       )
        ns.storenew = True
        self.log.debug("Created Nodeinfo object: %s" % ns)
        return ns 
    
    def listNodeinfos(self):
        return self.ic.listentities(Nodeinfo)
       
    def getNodeinfo(self, nodeinfoName):
        return self.ic.getentity(Nodeinfo, nodeinfoName)

    def deleteNodeinfo(self, nodeinfoName):
        self.ic.deleteentity(Nodeinfo, nodeinfoName)
    
    def storeNodeinfo(self, nodeinfo):
        nodeinfo.store(self.ic)
        

    ################################################################################
    #                        Nodeset-related calls
    ################################################################################ 
    def defineNodeset(self, 
                      name, 
                      owner, 
                      node_number, 
                      app_type, 
                      app_role,
                      app_peaceful = True,
                      app_lingertime = None,
                      app_killorder = None, 
                      nodeinfo = None,
                      environment = None,
                      description = None,
                      displayname = None,
                      url = None,
                      docurl = None,                      
                      ):

        ns = Nodeset( name=name, 
                      state='new',
                      state_reason='new',
                      owner=owner, 
                      node_number=node_number, 
                      app_type=app_type, 
                      app_role=app_role,
                      app_peaceful = app_peaceful,
                      app_lingertime = app_lingertime,
                      app_killorder = app_killorder,
                      nodeinfo = nodeinfo,
                      environment = environment,
                      description = description,
                      displayname = displayname,
                      url = url,
                      docurl = docurl
                       )
        ns.storenew = True
        self.log.debug("Created Nodeset object: %s" % ns)
        return ns 
    
    def listNodesets(self):
        return self.ic.listentities(Nodeset)
       
    def getNodeset(self, nodesetname):
        return self.ic.getentity(Nodeset, nodesetname)

    def deleteNodeset(self, nodesetname):
        self.ic.deleteentity(Nodeset, nodesetname)
    
    def storeNodeset(self, nodeset):
        nodeset.store(self.ic)

    ################################################################################
    #                        Environment-related calls
    ################################################################################ 
    def defineEnvironment(self, 
                          name, 
                          owner, 
                          packagelist = [], 
                          envmap = {}, 
                          files={}, 
                          command = None,
                          required_os = None,
                          builder_extra_args = None,
                          description = None,
                          displayname = None,
                          url = None,
                          docurl = None,                          
                          ):
        e = Environment(name, 
                        state='new', 
                        owner = owner, 
                        packagelist = packagelist, 
                        envmap = envmap,
                        files = files, 
                        command = command,
                        required_os = required_os,
                        builder_extra_args = builder_extra_args,
                        description = description,
                        displayname = displayname,
                        url = url,
                        docurl = docurl
                        )
        e.storenew = True
        self.log.debug("Creating Environment object: %s " % e)
        return e
    
    def storeEnvironment(self, environment):
        environment.store(self.ic)
    
    def listEnvironments(self):
        return self.ic.listentities(Environment)
       
    def getEnvironment(self, environmentname):
        return self.ic.getentity(Environment, environmentname)

    def deleteEnvironment(self, environmentname):
        self.ic.deleteentity(Environment , environmentname)


    ################################################################################
    #                        Request-related calls
    ################################################################################ 
    def defineRequest(self, 
                      name, 
                      owner,
                      cluster,
                      allocations,  
                      environments,
                      policy,
                      expiration,
                      project,
                      description = None,
                      displayname = None,
                      url = None,
                      docurl = None,
                      organization = None,
                      policy_user=None
                       ):
        '''
        :param str policy_user: The VC3 user name of the user trying this operation

        :return Request
        
        '''

        r = Request(name, 
                    state='new', 
                    owner=owner,
                    action='new',
                    state_reason='new',
                    cluster = cluster,           # name of abstract cluster specification
                    allocations  = allocations,   # list of allocation names
                    environments = environments,   # list of environments names
                    policy = policy, 
                    expiration = expiration,       # string representation of UTC time when request should be terminated. 
                    project = project,
                    description = description,
                    displayname = displayname,
                    url = url,
                    docurl = docurl,
                    organization = organization
                    )
        r.storenew = True
        self.log.debug("Creating Request object: %s " % r)
        return r
    
    def storeRequest(self, request, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            if request is not None and request.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the request owner")
            project = self.getProject(request.project)
            project_allocations = project.allocations
            for alloc in request.allocations:
                if alloc not in project_allocations:
                    raise PermissionDenied("{0} must be in project {1}".format(alloc,
                                                                               project.name))

        request.store(self.ic)


    def listRequests(self):
        return self.ic.listentities(Request)
       
    def getRequest(self, requestname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            request = self.ic.getentity(Request, requestname)
            if request is not None and request.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the request owner")
        return self.ic.getentity( Request, requestname)

    def deleteRequest(self, requestname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """

        request = self.getRequest(requestname)
        if request is not None:
            if policy_user is not None and request.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the request owner")
            else:

                try:
                    if request.cluster:
                        self.log.debug('Deleting cloned cluster template %s' % request.cluster)
                        cluster = self.ic.getentity(Cluster, request.cluster)

                    for nodeset in cluster.nodesets:
                        try:
                            self.log.debug('Deleting cloned nodeset %s' % nodeset)
                            self.deleteNodeset(nodeset)
                        except Exception, e:
                            self.log.error('Could not delete cloned nodeset %s' % nodeset)
                            raise e

                    self.deleteCluster(request.cluster)
                except Exception, e:
                    self.log.error('Could not delete cloned cluster %s' % request.cluster)
                    raise e

        self.ic.deleteentity( Request, requestname)

    def terminateRequest(self, requestname, policy_user=None):
        """
        :param str policy_user: The VC3 user name of the user trying this operation
        """
        if policy_user is not None:
            request = self.getRequest(requestname)
            if request is not None and request.owner != policy_user:
                raise PermissionDenied(policy_user + "is not the request owner")

        r = self.ic.getentity( Request, requestname)
        if r is not None:
            self.log.debug("Setting request action to terminate...")
            r.action = 'terminate'
            r.store(self.ic)
            print("Request.action set to terminate.")
        else:
            self.log.info("Request is None.")

    def getRequestStatus(self, requestname):
        r = self.ic.getentity( Request, requestname)
        out = (None, None)
        if r is not None:
            out = (r.statusraw, r.statusinfo)
        return out

    def getRequestState(self, requestname):
        r = self.ic.getentity( Request, requestname)
        out = (None, None)
        if r is not None:
            out = (r.state, r.state_reason)
        return out      

    def saveRequestAsBlueprint(self, requestid, newlabel):
        '''
        Take the specified request and store it as a re-usable blueprint with new label
        '''
        pass
    
    
    ################################################################################
    #                        Infrastructural calls
    ################################################################################ 
    def getQueuesConf(self, requestname, queuename):
        '''
        Get the queues.conf sections for the specified request and queuename
        
        May raise InfoMissingEntityException if Request doesn't exist. 
        
        '''
        r = self.getRequest(requestname)

        if not r.queuesconf:
            raise Exception('Request %s does not have a queues.conf defined' % requestname)

        try:
            buf   = StringIO.StringIO(self.decode(r.queuesconf))
            qconf = ConfigParser.ConfigParser()
            qconf.readfp(buf)

            return qconf.items(queuename)

        except Exception, e:
            self.log.error('Error decoding queues.conf of request %s' % requestname)
            raise e

    def getAuthConf(self, requestname, queuename):
        '''
        Get the auth.conf sections for the specified request and queuename
        '''
        r = self.getRequest(requestname)

        if not r.authconf:
            raise Exception('Request %s does not have a auth.conf defined' % requestname)

        try:
            buf   = StringIO.StringIO(self.decode(r.authconf))
            aconf = ConfigParser.ConfigParser()
            aconf.readfp(buf)

            return aconf.items(queuename)

        except Exception, e:
            self.log.error('Error decoding auth.conf of request %s' % requestname)
            raise e

    def getConfString(self, conftype, requestname ):
        '''
        Return string contents of specified conf type auth|queues
        '''
        r = self.getRequest(requestname)
        cs = ""
        if r:
            if conftype == 'queues':
                buf  = StringIO.StringIO(self.decode(r.queuesconf))
                cs = buf.read()
            elif conftype == 'auth':
                buf   = StringIO.StringIO(self.decode(r.authconf))
                cs = buf.read()
        else:
            self.log.debug("No request with name %s" % requestname)
        return cs


    def requestPairing(self, commonname):
        '''
        Create a request in the VC3 category to create a pairing setup protected by the supplied pairingcode.
        Master will see request, generate keypair, and place in infoservice w/ code. 
         
        '''
        code = self.ic.requestPairing(commonname)
        return code
        
    
    def getPairing(self, pairingcode):
        '''
        One-time only successful call. 
        Can be called unsuccessfully (i.e. during wait for request satisfaction) without harm. 
        Returns tuple of (pubsslkey, privsslkey)
         
        '''
        (cert, key) = self.ic.getPairing(pairingcode)
        return (cert, key)


##############################################
#        External Utility class methods. 
##############################################

    @classmethod
    def encode(self, string):
        return base64.b64encode(string)
    
    @classmethod
    def decode(self, string):
        return base64.b64decode(string)
       

    @classmethod
    def validate_ssh_pub_key(self, keystr):
        fh = tempfile.NamedTemporaryFile(prefix = "client-key", delete = False)
        try:
            fh.write(keystr)
            fh.close()

            with open(os.devnull) as fnull:
                status   = subprocess.call(['ssh-keygen', '-l', '-f', fh.name], stdout=fnull, stderr=fnull)
                return status == 0
        except Exception, e:
            raise e
        finally:
            os.remove(fh.name)


