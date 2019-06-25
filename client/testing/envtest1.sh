#!/bin/bash
#
# VC3 Client Test 
#

set -ex

CLIENT=~/git/vc3-client/vc3client/clientcli.py
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

$CLIENT $DEBUGS -c $CONFIG user-create --firstname Angus --lastname MacGuyver --email angus@bnl.gov --institution BNL angus

$CLIENT $DEBUGS -c $CONFIG project-create --owner angus --members angus  angusproject

$CLIENT $DEBUGS -c $CONFIG environment-create --owner angus --filesmap "~/git/vc3-client/testing/filea.txt=/etc/filea.txt,~/git/vc3-client/testing/fileb.txt=/etc/fileb.txt" angusenv1

$CLIENT $DEBUGS -c $CONFIG environment-list

