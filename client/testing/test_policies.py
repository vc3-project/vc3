"""
Unit tests for testing user policies as implemented in the vc3 client code
"""

import unittest
import ConfigParser
import sys
import os

import vc3client.client


vc3_client = None


def setupModule():
    """
    Create
    :return:
    """
    global vc3_client

    c = ConfigParser.SafeConfigParser()
    if 'VC3_CLIENT_CONFIG' in os.environ:
        c.readfp(open(os.environ['VC3_CLIENT_CONFIG']))
    else:
        c.readfp(open('./vc3-client.ini'))

    try:
        vc3_client = vc3client.client.VC3ClientAPI(c)
    except Exception as e:
        sys.stderr.write("Couldn't get vc3 client: {0}".format(e))
        raise e


# class TestUserPolicy(unittest.TestCase):
#     """
#     Class to test policy related to user operations
#     """
#
#     def setUp(self):
#         """
#         Setup vc3 infoservice for subsequent tests
#         :return:  None
#         """
#
#         new_user = vc3_client.defineUser(identity_id='test_id',
#                                          name='vc3name1',
#                                          first='First',
#                                          last='Last',
#                                          email='test@test.edu',
#                                          organization='Computation Institute',
#                                          displayname='test1')
#
#         vc3_client.storeUser(new_user)
#         self.__stored_user = new_user
#
#     def testViewProfile(self):
#         """
#         Test viewing profile operations
#         :return:  None
#         """
#         new_user2 = vc3_client.defineUser(identity_id='test_id2',
#                                           name='vc3name2',
#                                           first='First2',
#                                           last='Last2',
#                                           email='test2@test.edu',
#                                           organization='Computation Institute',
#                                           displayname='test2')
#         vc3_client.listUsers(policy_user=self.__stored_user)
#         # vc3_client.listUsers(policy_user=new_user2)
#
#     def tearDown(self):
#         """
#         Remove entities created for tests
#         :return:
#         """
#
#         vc3_client.deleteUser(self.__stored_user)


class TestAllocationPolicy(unittest.TestCase):
    """
    Class to test policy related to allocation operations
    """

    def setUp(self):
        """
        Setup vc3 infoservice for subsequent tests
        :return:  None
        """
        new_user = vc3_client.defineUser(identity_id='test_id',
                                         name='vc3name1',
                                         first='First',
                                         last='Last',
                                         email='test@test.edu',
                                         organization='Computation Institute',
                                         displayname='test1')

        vc3_client.storeUser(new_user)
        self.__stored_user = new_user

        new_user2 = vc3_client.defineUser(identity_id='test_id2',
                                          name='vc3name2',
                                          first='First2',
                                          last='Last2',
                                          email='test2@test.edu',
                                          organization='Computation Institute',
                                          displayname='test2')
        self.__unstored_user = new_user2

        resource = vc3_client.defineResource(name='resource',
                                             owner=new_user.name,
                                             accesstype='remote-batch',
                                             accessmethod='ssh',
                                             accessflavor='slurm',
                                             accesshost='login.host',
                                             accessport='3890',
                                             gridresource='gridresource',
                                             cloudspotprice='spotprice',
                                             cloudinstancetype='instance_type',
                                             mfa='mfa',
                                             description='testresource',
                                             displayname='displayname',
                                             url='url',
                                             docurl='docurl',
                                             organization='Computation Institute',
                                             )
        vc3_client.storeResource(resource)
        self.__resource = resource

    def tearDown(self):
        """
        Remove entities created for tests
        :return:
        """
        vc3_client.deleteUser(self.__stored_user.name)
        vc3_client.deleteResource(self.__resource.name)

    def testAllocationCreation(self):
        """
        Test policies related to allocation creation
        :return: None
        """

        # test allocation with user not in infosystem
        test_allocation = vc3_client.defineAllocation(
            name='testallocation1',
            owner=self.__unstored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc1',
            description='test allocation 1')

        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeAllocation(test_allocation,
                                       policy_user=self.__unstored_user.name)

        # test allocation creation with fake resource
        test_allocation = vc3_client.defineAllocation(
            name='testallocation1',
            owner=self.__stored_user.name,
            resource='fakeresource',
            accountname='dummy',
            displayname='testalloc1',
            description='test allocation 1')
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeAllocation(test_allocation,
                                       policy_user=self.__stored_user.name)

        # verify allocation can be created with right policies
        test_allocation = vc3_client.defineAllocation(
            name='testallocation1',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc1',
            description='test allocation 1')
        vc3_client.storeAllocation(test_allocation,
                                   policy_user=self.__stored_user.name)
        vc3_client.deleteAllocation(allocationname=test_allocation.name)

    def testAllocationEdit(self):
        """
        Test policies related to allocation editing
        :return: None
        """
        # verify allocation can be created with right policies
        test_allocation = vc3_client.defineAllocation(
            name='testallocation2',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc2',
            description='test allocation 2')
        vc3_client.storeAllocation(test_allocation,
                                   policy_user=self.__stored_user.name)

        # test editing displayname and description
        test_allocation = vc3_client.getAllocation(allocationname=test_allocation.name)
        test_allocation.displayname = 'newtestalloc2'
        test_allocation.description = 'newdescription'
        vc3_client.storeAllocation(test_allocation,
                                   policy_user=self.__stored_user.name)

        # test editing invalid stuff
        test_allocation.accountname = 'fakeaccount'
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeAllocation(test_allocation,
                                       policy_user=self.__stored_user.name)
        vc3_client.deleteAllocation(allocationname=test_allocation.name)

    def testAllocationDelete(self):
        """
        Test policies related to allocation deletion
        :return: None
        """

        test_allocation = vc3_client.defineAllocation(
            name='testallocation3',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc3',
            description='test allocation 3')
        vc3_client.storeAllocation(test_allocation,
                                   policy_user=self.__stored_user.name)

        # test deletion by non-owner
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteAllocation(test_allocation.name,
                                        policy_user=self.__unstored_user.name)

        # test deletion by valid owner
        vc3_client.deleteAllocation(test_allocation.name,
                                    policy_user=self.__stored_user.name)


class TestTemplatePolicy(unittest.TestCase):
    """
    Class to test policy related to cluster template operations
    """
    def setUp(self):
        """
        Setup infoservice for subsequent tests
        :return:  None
        """
        new_user = vc3_client.defineUser(identity_id='test_id',
                                         name='vc3name1',
                                         first='First',
                                         last='Last',
                                         email='test@test.edu',
                                         organization='Computation Institute',
                                         displayname='test1')

        vc3_client.storeUser(new_user)
        self.__stored_user = new_user

        new_user2 = vc3_client.defineUser(identity_id='test_id2',
                                          name='vc3name2',
                                          first='First2',
                                          last='Last2',
                                          email='test2@test.edu',
                                          organization='Computation Institute',
                                          displayname='test2')
        vc3_client.storeUser(new_user2)
        self.__stored_user2 = new_user2

        new_user3 = vc3_client.defineUser(identity_id='test_id3',
                                          name='vc3name3',
                                          first='First3',
                                          last='Last3',
                                          email='test3@test.edu',
                                          organization='Computation Institute',
                                          displayname='test3')
        vc3_client.storeUser(new_user3)
        self.__stored_user3 = new_user3

        new_user4 = vc3_client.defineUser(identity_id='test_id4',
                                          name='vc3name4',
                                          first='First4',
                                          last='Last4',
                                          email='test4@test.edu',
                                          organization='Computation Institute',
                                          displayname='test4')
        self.__unstored_user = new_user4

        resource = vc3_client.defineResource(name='resource',
                                             owner=new_user.name,
                                             accesstype='remote-batch',
                                             accessmethod='ssh',
                                             accessflavor='slurm',
                                             accesshost='login.host',
                                             accessport='3890',
                                             gridresource='gridresource',
                                             cloudspotprice='spotprice',
                                             cloudinstancetype='instance_type',
                                             mfa='mfa',
                                             description='testresource',
                                             displayname='displayname',
                                             url='url',
                                             docurl='docurl',
                                             organization='Computation Institute',
                                             )
        vc3_client.storeResource(resource)
        self.__resource = resource

        project = vc3_client.defineProject(name='project',
                                           owner=new_user3.name,
                                           members=[new_user3.name,
                                                    new_user2.name],
                                           description='project desc',
                                           displayname='test project',
                                           url='http://test.domain',
                                           docurl='http://test.domain/doc')
        vc3_client.storeProject(project)
        self.__project = project

        user_allocation = vc3_client.defineAllocation(
            name='testallocation3',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc3',
            description='test allocation 3')
        self.__user_allocation = user_allocation
        vc3_client.storeAllocation(user_allocation)

    def tearDown(self):
        """
        Remove entities created for tests
        :return:
        """
        vc3_client.deleteUser(self.__stored_user.name)
        vc3_client.deleteUser(self.__stored_user2.name)
        vc3_client.deleteUser(self.__stored_user3.name)
        vc3_client.deleteResource(self.__resource.name)
        vc3_client.deleteAllocation(self.__user_allocation.name)
        vc3_client.deleteProject(self.__project.name)

    def testTemplateCreation(self):
        """
        Test policies related to template creation
        :return: None
        """
        test_template = vc3_client.defineCluster(name='testtemplate1',
                                                 owner=self.__stored_user.name,
                                                 nodesets=[],
                                                 description='test desc',
                                                 displayname='test template 1',
                                                 url='http://local.host/',
                                                 docurl='http://local.host/docs')
        # check to make sure user not in infosystem fails
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeCluster(test_template,
                                    policy_user=self.__unstored_user.name)

        # check to make sure user without allocation fails
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeCluster(test_template,
                                    policy_user=self.__stored_user.name)

        # check to make sure user with allocation succeeds
        user1_alloc = vc3_client.getAllocation(allocationname=self.__user_allocation.name)
        user1_alloc.state = 'validated'
        vc3_client.storeAllocation(user1_alloc)
        vc3_client.storeCluster(test_template,
                                policy_user=self.__stored_user.name)
        vc3_client.deleteCluster(clustername=test_template.name)

        # check to make sure user in project succeeds
        test_template2 = vc3_client.defineCluster(name='testtemplate2',
                                                  owner=self.__stored_user2.name,
                                                  nodesets=[],
                                                  description='test desc',
                                                  displayname='test template 2',
                                                  url='http://local.host/',
                                                  docurl='http://local.host/docs')
        vc3_client.storeCluster(test_template2,
                                policy_user=self.__stored_user2.name)
        vc3_client.deleteCluster(clustername=test_template2.name)

    def testTemplateView(self):
        """
        Test policies related to template listing
        :return: None
        """
        # check to make sure user not in infosystem fails
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.listClusters(policy_user=self.__unstored_user.name)

        # check to make sure user with allocation succeeds
        user1_alloc = vc3_client.getAllocation(allocationname=self.__user_allocation.name)
        user1_alloc.state = 'validated'
        vc3_client.storeAllocation(user1_alloc)
        vc3_client.listClusters(policy_user=self.__stored_user.name)

        # check to make sure user in project succeeds
        vc3_client.listClusters(policy_user=self.__stored_user2.name)

    def testTemplateDelete(self):
        """
        Test policies related to template deletion
        :return: None
        """
        test_template = vc3_client.defineCluster(name='testtemplate1',
                                                 owner=self.__stored_user.name,
                                                 nodesets=[],
                                                 description='test desc',
                                                 displayname='test template 1',
                                                 url='http://local.host/',
                                                 docurl='http://local.host/docs')
        user1_alloc = vc3_client.getAllocation(allocationname=self.__user_allocation.name)
        user1_alloc.state = 'validated'
        vc3_client.storeAllocation(user1_alloc)
        vc3_client.storeCluster(test_template,
                                policy_user=self.__stored_user.name)

        # make sure invalid user fails
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteCluster(clustername=test_template.name,
                                     policy_user=self.__unstored_user.name)

        # make sure  user that isn't an owner fails
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteCluster(clustername=test_template.name,
                                     policy_user=self.__stored_user2.name)

        vc3_client.deleteCluster(clustername=test_template.name,
                                 policy_user=self.__stored_user.name)

    def testTemplateEdit(self):
        """
        Test policies related to template editing
        :return: None
        """
        test_template = vc3_client.defineCluster(name='testtemplate1',
                                                 owner=self.__stored_user.name,
                                                 nodesets=[],
                                                 description='test desc',
                                                 displayname='test template 1',
                                                 url='http://local.host/',
                                                 docurl='http://local.host/docs')
        user1_alloc = vc3_client.getAllocation(allocationname=self.__user_allocation.name)
        user1_alloc.state = 'validated'
        vc3_client.storeAllocation(user1_alloc)
        vc3_client.storeCluster(test_template,
                                policy_user=self.__stored_user.name)
        test_template = vc3_client.getCluster(clustername=test_template.name)

        # make sure non-owner can't modify cluster
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.addNodesetToCluster(nodesetname='testnodeset',
                                           clustername=test_template.name,
                                           policy_user=self.__stored_user2.name)

        # make sure owner can add nodeset
        vc3_client.addNodesetToCluster(nodesetname='testnodeset',
                                       clustername=test_template.name,
                                       policy_user=self.__stored_user.name)

        # make sure non-owner can't remove nodeset from cluster
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.removeNodesetFromCluster(nodesetname='testnodeset',
                                                clustername=test_template.name,
                                                policy_user=self.__stored_user2.name)

        # make sure owner can add nodeset
        vc3_client.removeNodesetFromCluster(nodesetname='testnodeset',
                                            clustername=test_template.name,
                                            policy_user=self.__stored_user.name)

        test_template.description = 'new description'
        # make sure non-owner can't remove nodeset from cluster
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeCluster(test_template,
                                    policy_user=self.__stored_user2.name)

        # make sure owner can add nodeset
        vc3_client.storeCluster(test_template,
                                policy_user=self.__stored_user.name)

        vc3_client.deleteCluster(clustername=test_template.name,
                                 policy_user=self.__stored_user.name)


class TestProjectPolicy(unittest.TestCase):
    """
    Class to test policy related to project operations
    """

    def setUp(self):
        """
        Setup vc3 client for subsequent tests
        :return:  None
        """

        new_user = vc3_client.defineUser(identity_id='test_id',
                                         name='vc3name1',
                                         first='First',
                                         last='Last',
                                         email='test@test.edu',
                                         organization='Computation Institute',
                                         displayname='test1')

        vc3_client.storeUser(new_user)
        self.__stored_user = new_user

        new_user2 = vc3_client.defineUser(identity_id='test_id2',
                                          name='vc3name2',
                                          first='First2',
                                          last='Last2',
                                          email='test2@test.edu',
                                          organization='Computation Institute',
                                          displayname='test2')
        vc3_client.storeUser(new_user2)
        self.__stored_user2 = new_user2

        new_user4 = vc3_client.defineUser(identity_id='test_id4',
                                          name='vc3name4',
                                          first='First4',
                                          last='Last4',
                                          email='test4@test.edu',
                                          organization='Computation Institute',
                                          displayname='test4')
        self.__unstored_user = new_user4

        resource = vc3_client.defineResource(name='resource',
                                             owner=new_user.name,
                                             accesstype='remote-batch',
                                             accessmethod='ssh',
                                             accessflavor='slurm',
                                             accesshost='login.host',
                                             accessport='3890',
                                             gridresource='gridresource',
                                             cloudspotprice='spotprice',
                                             cloudinstancetype='instance_type',
                                             mfa='mfa',
                                             description='testresource',
                                             displayname='displayname',
                                             url='url',
                                             docurl='docurl',
                                             organization='Computation Institute',
                                             )
        vc3_client.storeResource(resource)
        self.__resource = resource

        user_allocation = vc3_client.defineAllocation(
            name='testallocation3',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc3',
            description='testallocation3')
        user_allocation.state = 'validated'
        self.__user_allocation = user_allocation
        vc3_client.storeAllocation(user_allocation)

    def tearDown(self):
        """
        Remove entities created for tests
        :return:
        """

        vc3_client.deleteUser(self.__stored_user.name)
        vc3_client.deleteUser(self.__stored_user2.name)
        vc3_client.deleteResource(self.__resource.name)
        vc3_client.deleteAllocation(self.__user_allocation.name)

    def testProjectCreation(self):
        """
        Test policy for creation of projects

        :return: None
        """

        test_proj1 = vc3_client.defineProject(name='testproj1',
                                              owner=self.__stored_user.name,
                                              members=[],
                                              description=None,
                                              displayname=None,
                                              url=None,
                                              docurl=None,
                                              organization=None,
                                              policy_user=self.__stored_user.name)

        # make sure user not in system can't create project
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeProject(test_proj1,
                                    policy_user=self.__unstored_user.name)

        # make sure user without allocation can't create project
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeProject(test_proj1,
                                    policy_user=self.__stored_user2.name)

        vc3_client.storeProject(test_proj1,
                                policy_user=self.__stored_user.name)

        vc3_client.deleteProject(projectname=test_proj1.name,
                                 policy_user=self.__stored_user.name)

    def testProjectView(self):
        """
        Test policies for viewing a project

        :return: None
        """

        # make sure user not in system can't list projects
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.listProjects(policy_user=self.__unstored_user.name)

        # verify view with valid user
        vc3_client.listProjects(policy_user=self.__stored_user.name)

    def testProjectEdit(self):
        """
        Test policies for editing a project

        :return: None
        """
        test_proj1 = vc3_client.defineProject(name='testproj1',
                                              owner=self.__stored_user.name,
                                              members=[self.__stored_user.name],
                                              description=None,
                                              displayname=None,
                                              url=None,
                                              docurl=None,
                                              organization=None,
                                              policy_user=self.__stored_user.name)

        vc3_client.storeProject(test_proj1,
                                policy_user=self.__stored_user.name)

        test_proj1 = vc3_client.getProject(projectname=test_proj1.name)
        # verify non-owner can't edit
        test_proj1.displayname = 'invalidname'
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeProject(test_proj1,
                                    policy_user=self.__stored_user2.name)

        # verify that owner can edit
        test_proj1.displayname = 'newname'
        vc3_client.storeProject(test_proj1,
                                policy_user=self.__stored_user.name)

        # verify owner can add members
        vc3_client.addUserToProject(self.__stored_user2.name,
                                    test_proj1.name,
                                    policy_user=self.__stored_user.name)

        # verify owner can remove members
        vc3_client.removeUserFromProject(self.__stored_user2.name,
                                         test_proj1.name,
                                         policy_user=self.__stored_user.name)

        # verify user not in infosystem can't add members
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.addUserToProject(self.__stored_user2.name,
                                        test_proj1.name,
                                        policy_user=self.__unstored_user.name)

        # verify user that's not the owner can't add members
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.addUserToProject(self.__stored_user2.name,
                                        test_proj1.name,
                                        policy_user=self.__stored_user2.name)

        # verify members can remove themselves
        vc3_client.addUserToProject(self.__stored_user2.name,
                                    test_proj1.name,
                                    policy_user=self.__stored_user.name)
        vc3_client.removeUserFromProject(self.__stored_user2.name,
                                         test_proj1.name,
                                         policy_user=self.__stored_user2.name)

        # verify members can add their allocations
        vc3_client.addAllocationToProject(self.__user_allocation.name,
                                          test_proj1.name,
                                          policy_user=self.__stored_user.name)

        # verify members can remove their allocations
        vc3_client.removeAllocationFromProject(self.__user_allocation.name,
                                               test_proj1.name,
                                               policy_user=self.__stored_user.name)

        # verify users can't add random allocations
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.addAllocationToProject(self.__user_allocation.name,
                                              test_proj1.name,
                                              policy_user=self.__stored_user2.name)

        vc3_client.deleteProject(projectname=test_proj1.name,
                                 policy_user=self.__stored_user.name)

    def testProjectDelete(self):
        """
        Test policies related to project deletion
        :return: None
        """

        test_proj1 = vc3_client.defineProject(name='testproj1',
                                              owner=self.__stored_user.name,
                                              members=[],
                                              description=None,
                                              displayname=None,
                                              url=None,
                                              docurl=None,
                                              organization=None,
                                              policy_user=self.__stored_user.name)

        vc3_client.storeProject(test_proj1,
                                policy_user=self.__stored_user.name)

        # test deletion by non-owner
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteProject(projectname=test_proj1.name,
                                     policy_user=self.__stored_user2.name)

        # test deletion by valid owner
        vc3_client.deleteProject(projectname=test_proj1.name,
                                 policy_user=self.__stored_user.name)


class TestRequestPolicy(unittest.TestCase):
    """
    Class to test policy related to cluster request operations
    """
    def setUp(self):
        """
        Setup vc3 info server for subsequent tests
        :return:  None
        """
        new_user = vc3_client.defineUser(identity_id='test_id',
                                         name='vc3name1',
                                         first='First',
                                         last='Last',
                                         email='test@test.edu',
                                         organization='Computation Institute',
                                         displayname='test1')

        vc3_client.storeUser(new_user)
        self.__stored_user = new_user

        new_user2 = vc3_client.defineUser(identity_id='test_id2',
                                          name='vc3name2',
                                          first='First2',
                                          last='Last2',
                                          email='test2@test.edu',
                                          organization='Computation Institute',
                                          displayname='test2')
        vc3_client.storeUser(new_user2)
        self.__stored_user2 = new_user2

        new_user4 = vc3_client.defineUser(identity_id='test_id4',
                                          name='vc3name4',
                                          first='First4',
                                          last='Last4',
                                          email='test4@test.edu',
                                          organization='Computation Institute',
                                          displayname='test4')
        self.__unstored_user = new_user4

        resource = vc3_client.defineResource(name='resource',
                                             owner=new_user.name,
                                             accesstype='remote-batch',
                                             accessmethod='ssh',
                                             accessflavor='slurm',
                                             accesshost='login.host',
                                             accessport='3890',
                                             gridresource='gridresource',
                                             cloudspotprice='spotprice',
                                             cloudinstancetype='instance_type',
                                             mfa='mfa',
                                             description='testresource',
                                             displayname='displayname',
                                             url='url',
                                             docurl='docurl',
                                             organization='Computation Institute',
                                             )
        vc3_client.storeResource(resource)
        self.__resource = resource

        user_allocation = vc3_client.defineAllocation(
            name='testallocation3',
            owner=self.__stored_user.name,
            resource=self.__resource.name,
            accountname='dummy',
            displayname='testalloc3',
            description='testallocation3')
        user_allocation.state = 'validated'
        self.__user_allocation = user_allocation
        vc3_client.storeAllocation(user_allocation)

        test_template = vc3_client.defineCluster(name='testtemplate1',
                                                 owner=self.__stored_user.name,
                                                 nodesets=[],
                                                 description='test desc',
                                                 displayname='test template 1',
                                                 url='http://local.host/',
                                                 docurl='http://local.host/docs')

        # check to make sure user with allocation succeeds
        vc3_client.storeCluster(test_template,
                                policy_user=self.__stored_user.name)
        self.__stored_template = test_template

        project = vc3_client.defineProject(name='project',
                                           owner=new_user.name,
                                           members=[new_user.name,
                                                    new_user2.name],
                                           description='project desc',
                                           displayname='test project',
                                           url='http://test.domain',
                                           docurl='http://test.domain/doc')
        vc3_client.storeProject(project)
        project = vc3_client.getProject(projectname=project.name)
        vc3_client.addAllocationToProject(self.__user_allocation.name,
                                          project.name,
                                          policy_user=self.__stored_user.name)
        self.__stored_project = project

    def tearDown(self):
        """
        Remove entities created for tests
        :return:
        """
        vc3_client.deleteUser(self.__stored_user.name)
        vc3_client.deleteUser(self.__stored_user2.name)
        vc3_client.deleteResource(self.__resource.name)
        vc3_client.deleteAllocation(self.__user_allocation.name)
        vc3_client.deleteCluster(self.__stored_template.name)
        vc3_client.deleteProject(self.__stored_project.name)

    def testRequestCreation(self):
        """
        Test policies for creating a request

        :return: None
        """

        test_request = vc3_client.defineRequest(name='testrequest1',
                                                owner=self.__stored_user.name,
                                                cluster=self.__stored_template.name,
                                                allocations=[self.__user_allocation.name],
                                                environments='',
                                                policy='',
                                                expiration='',
                                                project=self.__stored_project.name,
                                                description='test request 1',
                                                displayname='test request 1',
                                                url=None,
                                                docurl=None,
                                                organization=None,
                                                policy_user=self.__stored_user.name)

        # make sure user not in system can't create project
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeRequest(test_request,
                                    policy_user=self.__unstored_user.name)

        # make sure user without allocation can't create project
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.storeRequest(test_request,
                                    policy_user=self.__stored_user2.name)

        vc3_client.storeRequest(test_request,
                                policy_user=self.__stored_user.name)

        vc3_client.deleteRequest(requestname=test_request.name,
                                 policy_user=self.__stored_user.name)

    def testRequestGet(self):
        """
        Test policies for viewing a request

        :return: None
        """

        test_request = vc3_client.defineRequest(name='testrequest1',
                                                owner=self.__stored_user.name,
                                                cluster=self.__stored_template.name,
                                                allocations=[self.__user_allocation.name],
                                                environments='',
                                                policy='',
                                                expiration='',
                                                project=self.__stored_project.name,
                                                description='test request 1',
                                                displayname='test request 1',
                                                url=None,
                                                docurl=None,
                                                organization=None,
                                                policy_user=self.__stored_user.name)

        vc3_client.storeRequest(test_request,
                                policy_user=self.__stored_user.name)

        # make sure user not in system can't get request info
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.getRequest(requestname=test_request.name,
                                  policy_user=self.__unstored_user.name)

        # make sure user that's not the owner can't get request info
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.getRequest(requestname=test_request.name,
                                  policy_user=self.__stored_user2.name)

        # verify view with owner user
        vc3_client.getRequest(requestname=test_request.name,
                              policy_user=self.__stored_user.name)

        vc3_client.deleteRequest(requestname=test_request.name,
                                 policy_user=self.__stored_user.name)

    def testRequestDeletion(self):
        """
        Test policies for deleting a request

        :return: None
        """

        test_request = vc3_client.defineRequest(name='testrequest1',
                                                owner=self.__stored_user.name,
                                                cluster=self.__stored_template.name,
                                                allocations=[self.__user_allocation.name],
                                                environments='',
                                                policy='',
                                                expiration='',
                                                project=self.__stored_project.name,
                                                description='test request 1',
                                                displayname='test request 1',
                                                url=None,
                                                docurl=None,
                                                organization=None,
                                                policy_user=self.__stored_user.name)

        vc3_client.storeRequest(test_request,
                                policy_user=self.__stored_user.name)

        # make sure user not in system can't delete reqiest
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteRequest(requestname=test_request.name,
                                     policy_user=self.__unstored_user.name)

        # make sure user other than owner can't delete request
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.deleteRequest(requestname=test_request.name,
                                     policy_user=self.__stored_user2.name)

        vc3_client.deleteRequest(requestname=test_request.name,
                                 policy_user=self.__stored_user.name)

    def testRequestTermination(self):
        """
        Test policies for terminating a request

        :return: None
        """

        test_request = vc3_client.defineRequest(name='testrequest1',
                                                owner=self.__stored_user.name,
                                                cluster=self.__stored_template.name,
                                                allocations=[self.__user_allocation.name],
                                                environments='',
                                                policy='',
                                                expiration='',
                                                project=self.__stored_project.name,
                                                description='test request 1',
                                                displayname='test request 1',
                                                url=None,
                                                docurl=None,
                                                organization=None,
                                                policy_user=self.__stored_user.name)

        vc3_client.storeRequest(test_request,
                                policy_user=self.__stored_user.name)

        # make sure user not in system can't delete reqiest
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.terminateRequest(requestname=test_request.name,
                                        policy_user=self.__unstored_user.name)

        # make sure user other than owner can't delete request
        with self.assertRaises(vc3client.client.PermissionDenied):
            vc3_client.terminateRequest(requestname=test_request.name,
                                        policy_user=self.__stored_user2.name)

        vc3_client.terminateRequest(requestname=test_request.name,
                                    policy_user=self.__stored_user.name)
        vc3_client.deleteRequest(requestname=test_request.name,
                                 policy_user=self.__stored_user.name)
