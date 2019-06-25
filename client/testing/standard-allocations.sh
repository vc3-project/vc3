#!/bin/bash

source ./standard-common-config.sh

# Create allocation
#Allocation( name=lincolnb.uchicago-midway state=authconfigured owner=lincolnb resource=uchicago-midway type=unlimited accountname=lincolnb quantity=None units=None sectype=ssh-rsa description=Lincolns midway account displayname=lincolnb-midway url=None docurl=None )
RUN_CHECK_CLIENT allocation-create --owner lincolnb --resource uchicago-midway --accountname lincolnb --description "My Midway account at RCC" --displayname lincolnb-midway lincolnb.uchicago-midway 

RUN_CHECK_CLIENT allocation-validate --allocationname lincolnb.uchicago-midway 



RUN_CHECK_CLIENT allocation-create --owner btovar --resource ndccl --accountname btovar --description "ND CCL" --displayname btovar-ndccl btovar.ndccl

RUN_CHECK_CLIENT allocation-validate --allocationname btovar.ndccl

RUN_CHECK_CLIENT project-addallocation btovar btovar.ndccl



RUN_CHECK_CLIENT allocation-create --owner khurtado --resource osg-connect --accountname khurtado --description "OSG Connect" --displayname khurtado-osgconnect khurtado.osg-connect

RUN_CHECK_CLIENT allocation-validate --allocationname khurtado.osg-connect

