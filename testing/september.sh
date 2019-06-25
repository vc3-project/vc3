#!/bin/bash -x
#
# VC3 Client Test 
#

set -x

export PATH=$PATH:~/.local/bin

CLIENT=vc3-client
#CONFIG=/etc/vc3/vc3-client.conf
CONFIG=~/git/vc3-client/etc/vc3-client.conf
#CONFIG=~/vc3/etc/vc3-client.conf


# DEFAULT values
DEBUG=0
DEBUGS=""

CONDOR_COLLECTOR=condor.virtualclusters.org

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


# Users
$CLIENT $DEBUGS -c $CONFIG user-create --firstname Lincoln --lastname Bryant --email lincolnb@uchicago.edu --institution UChicago lincolnb
$CLIENT $DEBUGS -c $CONFIG user-create --firstname Benedikt --lastname Riedel --email briedel@uchicago.edu --institution UChicago briedel
$CLIENT $DEBUGS -c $CONFIG user-create --firstname Judith --lastname Stephen --email jlstephen@uchicago.edu --institution UChicago jlstephen

# New project
$CLIENT $DEBUGS -c $CONFIG project-create --owner lincolnb --members lincolnb,briedel SPT

# add user to existing project
$CLIENT $DEBUGS -c $CONFIG project-adduser SPT jlstephen

# Create resource
$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost midway-login1.rcc.uchicago.edu --accessport 22 uchicago-midway
$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor condor --accesshost condor.grid.uchicago.edu --accessport 22 uchicago-coreos
$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost cori.nersc.gov --accessport 22 nersc-cori

# Create allocation
$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource uchicago-midway --accountname lincolnb lincolnb.uchicago-midway
$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource uchicago-coreos --accountname lincolnb lincolnb.uchicago-coreos
$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource nersc-cori --accountname briedel briedel.nersc-cori

# Create environment
# below is likely wrong, as the file mappings go to /etc. Most likely, that will result in a permission denied error when writing the file.
# $CLIENT $DEBUGS -c $CONFIG environment-create --owner lincolnb --filesmap "~/git/vc3-client/testing/filea.txt=/etc/filea.txt,~/git/vc3-client/testing/fileb.txt=/etc/fileb.txt" lincolnb-env1

# we simply use the environment to send the password file (temporal solution for the demo)
# make sure the name of this environment is the environment for the nodesets that need to talk to the condor collector
PASSWORD_REMOTE_NAME=mycondorpassword
$CLIENT $DEBUGS -c $CONFIG environment-create\
    --owner      lincolnb\
    --envvar     VC3_CONDOR_PASSWORD_FILE=${PASSWORD_REMOTE_NAME}\
    --filesmap   "~/git/vc3-client/testing/mycondorpassword=${PASSWORD_REMOTE_NAME}"\
    condor-glidein-password-env1

# List environments
#$CLIENT $DEBUGS -c $CONFIG environment-list
# Node set for the virtual cluster
# Only one nodeset per cluster for now. Just workers..
#$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner lincolnb --node_number 1 --app_type htcondor --app_role head-node --environment condor-glidein-password-env1 htcondor-head-1
$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner lincolnb --node_number 10 --app_type htcondor --app_role worker-nodes --environment condor-glidein-password-env1 htcondor-workers-1
# virtual cluster holder
$CLIENT $DEBUGS -c $CONFIG cluster-create --owner lincolnb htcondor-10workers

# Add nodeset to cluster
$CLIENT $DEBUGS -c $CONFIG cluster-addnodeset htcondor-10workers htcondor-workers-1


# Create request
$CLIENT $DEBUGS -c $CONFIG request-create --project SouthPoleTelescope --owner lincolnb --cluster htcondor-10workers --allocations lincolnb.uchicago-midway,lincolnb.uchicago-coreos september-demo-request

# Terminate a request
# $CLIENT $DEBUGS -c $CONFIG request-terminate --requestname september-demo-request
