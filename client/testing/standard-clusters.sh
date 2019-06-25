#!/bin/bash
source ./standard-common-config.sh


RUN_CHECK_CLIENT nodeset-create --owner btovar --node_number 0 --app_type htcondor --app_role worker-nodes --app_killorder newest --displayname="htcondor" btovar-htcondor-nodeset
RUN_CHECK_CLIENT cluster-create --owner btovar --description "htcondor" --displayname="htcondor" btovar-htcondor-cluster --public

RUN_CHECK_CLIENT cluster-addnodeset btovar-htcondor-cluster btovar-htcondor-nodeset


RUN_CHECK_CLIENT nodeset-create --owner btovar --node_number 0 --app_type spark --app_role worker-nodes --app_killorder newest --displayname="spark" btovar-spark-nodeset
RUN_CHECK_CLIENT cluster-create --owner btovar --description "spark" --displayname="spark" btovar-spark-cluster --public
RUN_CHECK_CLIENT cluster-addnodeset btovar-spark-cluster btovar-spark-nodeset


RUN_CHECK_CLIENT nodeset-create --owner btovar --node_number 0 --app_type workqueue --app_role worker-nodes --app_killorder newest --displayname="workqueue" btovar-workqueue-nodeset
RUN_CHECK_CLIENT cluster-create --owner btovar --description "workqueue" --displayname="workqueue" btovar-workqueue-cluster --public
RUN_CHECK_CLIENT cluster-addnodeset btovar-workqueue-cluster btovar-workqueue-nodeset


RUN_CHECK_CLIENT nodeset-create --owner btovar --node_number 0 --app_type jupyter --app_role worker-nodes --app_killorder newest --displayname="jupyter" btovar-jupyter-nodeset
RUN_CHECK_CLIENT cluster-create --owner btovar --description "jupyter" --displayname="jupyter" btovar-jupyter-cluster --public
RUN_CHECK_CLIENT cluster-addnodeset btovar-jupyter-cluster btovar-jupyter-nodeset

