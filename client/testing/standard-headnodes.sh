#!/bin/bash
source ./standard-common-config.sh

RUN_CHECK_CLIENT nodeset-create --owner btovar --node_number 1 --app_type htcondor --app_role head-node --displayname="htcondor headnode" vc3-headnode-htcondor

