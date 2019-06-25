Introduction
============

This is the command-line client used to create a virtual cluster through the VC3 infrastructure.

Creating a request
==================
Assuming a configuration in /etc/vc3-client.conf, and a defined resource, you can create a full request via:
::
        vc3-client -c /etc/vc3-client.conf user-create --firstname User --lastname LastName --email user@institution.edu --institution Institution user
        # To list your user:
        vc3-client -c /etc/vc3-client.conf user-list

        # Creating a project:
        vc3-client -c /etc/vc3-client.conf project-create --owner angus --members angus angusproject

        # Adding a user to a project:
        vc3-client -c /etc/vc3-client.conf project-create --owner user --members user userproject
        # Listing the project:
        vc3-client -c /etc/vc3-client.conf project-list

        # Creating a resource:
        vc3-client -c /etc/vc3-client.conf resource-create --owner admin --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost yourhost.gov --accessport 22 resourcename
        # To see the resource
        vc3-client -c /etc/vc3-client.conf resource-list

        # To create an allocation
        vc3-client -c /etc/vc3-client.conf allocation-create --owner user --resource resourcename --accountname user user.resourcename

        # Create a nodeset
        vc3-client -c /etc/vc3-client.conf nodeset-create --owner user --node_number 1 --app_type htcondor --app_role head-node htcondor-head.1
        vc3-client -c /etc/vc3-client.conf nodeset-create --owner user --node_number 10 --app_type htcondor --app_role worker-nodes htcondor-workers.1
        # List your node:
        vc3-client -c /etc/vc3-client.conf nodeset-list

        # Create a cluster
        vc3-client -c /etc/vc3-client.conf cluster-create --owner user htcondor-scn-10workers
        # List your cluster
        vc3-client -c /etc/vc3-client.conf cluster-list

        # Create environment for the cluster
        vc3-client -c /etc/vc3-client.conf environment-create --owner angus --filesmap "~/git/vc3-client/testing/filea.txt=/etc/filea.txt,~/git/vc3-client/testing/fileb.txt=/etc/fileb.txt" angusenv1
        # List environment
        vc3-client -c /etc/vc3-client.conf environment-list

        # Create request
        vc3-client -c /etc/vc3-client.conf request-create --owner user --cluster htcondor-scn-10workers --allocations user.requestname --environments angusenv1 user.request1

