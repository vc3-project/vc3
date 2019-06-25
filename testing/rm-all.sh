#!/bin/bash -x

# stop requests and wait until they are in terminated state, then delete
requests=$(vc3-client -c /etc/vc3/vc3-client.conf request-list | grep -v "terminated" | awk '{print $2}' | cut -d'=' -f2)

for request in $requests; do 
    vc3-client -c /etc/vc3/vc3-client.conf request-terminate --requestname $request;
done

for request in $requests;do 
    terminated=0;
    while [[ $terminated == 0 ]]; do 
        sleep 10;
        vc3-client -c /etc/vc3/vc3-client.conf request-list --requestname $request | grep terminated
        if [[ $? == 0 ]]; then 
            terminated=1;
        fi
    done
done


# remove everything else except users
for j in environment cluster nodeset allocation project resource request; do
   for i in $(vc3-client --conf /etc/vc3/vc3-client.conf $j-list | awk '{print $2}' | cut -d'=' -f2); do
     vc3-client --conf /etc/vc3/vc3-client.conf $j-delete $i
   done
done
