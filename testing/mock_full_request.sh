#! /bin/sh

set -ex

requestid=MY_REQUEST
owner=jhover
#config=/etc/vc3/vc3-client.conf
config=~/git/vc3-client/etc/vc3-client.conf

vc3-client -c ${config} user-create --firstname John --lastname Hover --email jhover@bnl.gov --institution BNL jhover

vc3-client -c ${config} project-create --owner jhover --members jhover jhover

vc3-client -c ${config} resource-create --owner ${owner} --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost resource.org --accessport 1234 RESOURCE_1

vc3-client -c ${config} resource-create --owner ${owner} --accesstype batch --accessmethod ssh --accessflavor sge --accesshost otherresource.org --accessport 1234 RESOURCE_2

vc3-client -c ${config} allocation-create --owner ${owner} --resource RESOURCE_1 --accountname vc3-${owner} ALLOCATION_1

vc3-client -c ${config} allocation-create --owner ${owner} --resource RESOURCE_2 --accountname vc3-${owner} ALLOCATION_2

vc3-client -c ${config} environment-create --owner ${owner} --packages cctools --envvar HELLO=world ENVIRONMENT_1

vc3-client -c ${config} nodeset-create --owner ${owner} --node_number 1 --app_type APP_TYPE --app_role APP_ROLE NODESET_1 --environment ENVIRONMENT_1

vc3-client -c ${config} cluster-create --owner ${owner} --nodesets NODESET_1 CLUSTER_1

vc3-client -c ${config} request-create --owner ${owner} --cluster CLUSTER_1 --project ${owner} --allocations ALLOCATION_1,ALLOCATION_2 ${requestid}


vc3-client -c ${config} allocation-list

vc3-client -c ${config} resource-list

vc3-client -c ${config} environment-list

vc3-client -c ${config} nodeset-list

vc3-client -c ${config} cluster-list

vc3-client -c ${config} request-list

