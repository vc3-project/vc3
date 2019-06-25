#!/bin/bash
#
# VC3 Client Test 
#

set -ex

CLIENT=vc3-client
#CONFIG=/etc/vc3/vc3-client.conf
CONFIG=~/git/vc3-client/etc/vc3-client.conf


# DEFAULT values
DEBUG=0
DEBUGS=""

# read the options
ARGS=`getopt -o d -l debug -- "$@"`  
eval set -- "$ARGS"

# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -d|--debug) DEBUG=1 ; shift ;;
        --) shift ; break ;;
        *) echo "Internal error!" ; exit 1 ;;
    esac
done

# set variables accordingly...
if [ "$DEBUG" = "1" ] ; then
   DEBUGS=" -d "
else
   DEBUGS=""
fi

$CLIENT $DEBUGS -c $CONFIG user-create --firstname John --lastname Hover --email jhover@bnl.gov --institution BNL jhover

$CLIENT $DEBUGS -c $CONFIG user-create --firstname Angus --lastname MacGuyver --email angus@bnl.gov --institution BNL --identity_id "angus1@globus.org" angus

$CLIENT $DEBUGS -c $CONFIG user-create --firstname John --lastname Hover --email jhover@bnl.gov --institution BNL adminjhover

$CLIENT $DEBUGS -c $CONFIG user-list

$CLIENT $DEBUGS -c $CONFIG user-list --user jhover



$CLIENT $DEBUGS -c $CONFIG project-create --owner angus --members angus  angusproject

$CLIENT $DEBUGS -c $CONFIG project-create --owner jhover --members jhover  jhoverproject

$CLIENT $DEBUGS -c $CONFIG project-adduser jhoverproject jhover

$CLIENT $DEBUGS -c $CONFIG project-removeuser jhoverproject jhover

$CLIENT $DEBUGS -c $CONFIG project-addallocation jhoverproject jhover.sdcc-ic

$CLIENT $DEBUGS -c $CONFIG project-addallocation jhoverproject jhover.sdcc-icx

$CLIENT $DEBUGS -c $CONFIG project-removeallocation jhoverproject jhover.sdcc-icx

$CLIENT $DEBUGS -c $CONFIG project-list

$CLIENT $DEBUGS -c $CONFIG project-list --project jhoverproject



$CLIENT $DEBUGS -c $CONFIG resource-create  --owner adminjhover --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost griddev03.racf.bnl.gov --accessport 22 sdcc-ic

$CLIENT $DEBUGS -c $CONFIG resource-list

$CLIENT $DEBUGS -c $CONFIG resource-list --resource sdcc-ic



$CLIENT $DEBUGS -c $CONFIG allocation-create --owner jhover --resource sdcc-ic --accountname jhover jhover.sdcc-ic

$CLIENT $DEBUGS -c $CONFIG allocation-list

$CLIENT $DEBUGS -c $CONFIG allocation-list --allocation jhover.sdcc-ic

$CLIENT $DEBUGS -c $CONFIG allocation-getpubtoken --allocation jhover.sdcc-ic



$CLIENT $DEBUGS -c $CONFIG environment-create --owner angus --filesmap "~/git/vc3-client/testing/filea.txt=/etc/filea.txt,~/git/vc3-client/testing/fileb.txt=/etc/fileb.txt" angusenv1

$CLIENT $DEBUGS -c $CONFIG environment-list

$CLIENT $DEBUGS -c $CONFIG environment-list --environment angusenv1



$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner jhover --node_number 1 --app_type htcondor --app_role head-node --environment angusenv1 htcondor-head.1

$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner jhover --node_number 10 --app_type htcondor --app_role worker-nodes htcondor-workers.1

$CLIENT $DEBUGS -c $CONFIG nodeset-list

$CLIENT $DEBUGS -c $CONFIG nodeset-list --node htcondor-workers.1



$CLIENT $DEBUGS -c $CONFIG cluster-create --owner jhover htcondor-scn-10workers

$CLIENT $DEBUGS -c $CONFIG cluster-list

$CLIENT $DEBUGS -c $CONFIG cluster-list --cluster htcondor-scn-10workers

$CLIENT $DEBUGS -c $CONFIG cluster-addnodeset htcondor-scn-10workers htcondor-workers.1

$CLIENT $DEBUGS -c $CONFIG cluster-addnodeset htcondor-scn-10workers htcondor-workers.2

$CLIENT $DEBUGS -c $CONFIG cluster-removenodeset htcondor-scn-10workers htcondor-workers.2



$CLIENT $DEBUGS -c $CONFIG request-create --owner jhover --cluster htcondor-scn-10workers --project jhover --allocations jhover.sdcc-ic jhover.request1

$CLIENT $DEBUGS -c $CONFIG request-list

$CLIENT $DEBUGS -c $CONFIG request-list --request jhover.request1

$CLIENT $DEBUGS -c $CONFIG request-state --request jhover.request1

$CLIENT $DEBUGS -c $CONFIG request-status --request jhover.request1

$CLIENT $DEBUGS -c $CONFIG request-terminate --request jhover.request1


# pin=$($CLIENT $DEBUGS -c $CONFIG pairing-create jhover.pair1)

# $CLIENT $DEBUGS -c $CONFIG pairing-retrieve ${pin}

