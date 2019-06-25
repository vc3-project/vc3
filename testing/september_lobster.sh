#!/bin/bash -x
#
# VC3 Client Test 
#

set -xe

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
$CLIENT $DEBUGS -c $CONFIG user-create --firstname Kenyi --lastname Hurtado --email khurtado@nd.edu --institution NotreDame khurtado

# New project
$CLIENT $DEBUGS -c $CONFIG project-create --owner khurtado --members khurtado,lincolnb LOBSTER

# Create resource
$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost midway-login1.rcc.uchicago.edu --accessport 22 uchicago-midway
#$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor condor --accesshost condor.grid.uchicago.edu --accessport 22 uchicago-coreos
#$CLIENT $DEBUGS -c $CONFIG resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost cori.nersc.gov --accessport 22 nersc-cori

# Create allocation
$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource uchicago-midway --accountname lincolnb lincolnb.uchicago-midway
#$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource uchicago-coreos --accountname lincolnb lincolnb.uchicago-coreos
#$CLIENT $DEBUGS -c $CONFIG allocation-create --owner lincolnb --resource nersc-cori --accountname briedel briedel.nersc-cori

# Create environment
# below is likely wrong, as the file mappings go to /etc. Most likely, that will result in a permission denied error when writing the file.
# $CLIENT $DEBUGS -c $CONFIG environment-create --owner lincolnb --filesmap "~/git/vc3-client/testing/filea.txt=/etc/filea.txt,~/git/vc3-client/testing/fileb.txt=/etc/fileb.txt" lincolnb-env1

$CLIENT $DEBUGS -c $CONFIG environment-create\
    --owner      khurtado\
    --packages   cctools-statics\
    --extra-args='--var GLIDEIN_Proxy_URL=http://cache01.hep.wisc.edu:3128'\
    --extra-args='--revar TMPDIR'\
    --command    "work_queue_worker -M lobster_khurtado_mc_v2 -t 300 --cores 1 --memory 2000 --workdir=/scratch/midway/lincolnb"\
    khurtado-env3

# List environments
#$CLIENT $DEBUGS -c $CONFIG environment-list
# Node set for the virtual cluster
# Only one nodeset per cluster for now. Just workers..
#$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner lincolnb --node_number 1 --app_type htcondor --app_role head-node --environment lincolnb-env1 htcondor-head-1
$CLIENT $DEBUGS -c $CONFIG nodeset-create --owner khurtado --node_number 10 --app_type htcondor --app_role worker-nodes --environment khurtado-env3 htcondor-workers-1
# virtual cluster holder
$CLIENT $DEBUGS -c $CONFIG cluster-create --owner khurtado htcondor-10workers

# Add nodeset to cluster
$CLIENT $DEBUGS -c $CONFIG cluster-addnodeset htcondor-10workers htcondor-workers-1


# Create request
$CLIENT $DEBUGS -c $CONFIG request-create --owner khurtado --cluster htcondor-10workers --project lobster --allocations lincolnb.uchicago-midway september-demo-request-lobster3

# Terminate a request
#$CLIENT $DEBUGS -c $CONFIG request-terminate --requestname september-demo-request-lobster
