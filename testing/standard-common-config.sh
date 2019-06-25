#! /bin/bash

CLIENT=vc3-client
CONFIG=/etc/vc3/vc3-client.conf
#CONFIG=~/git/vc3-client/etc/vc3-client.conf
#CONFIG=~/vc3/etc/vc3-client.conf

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


RUN_CHECK_CLIENT () {

    set -x
    $CLIENT $DEBUGS -c $CONFIG "$@"
    status=$?
    set +x

    # if error, and entity does not already exist, exit:
    if [ "$status" != 0 -a "$status" != 2 ]
    then
        exit $status
    fi
}


