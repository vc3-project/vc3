#!/bin/bash

source ./standard-common-config.sh

RUN_CHECK_CLIENT project-create --owner lincolnb --members lincolnb lincolnb
RUN_CHECK_CLIENT project-create --owner jvan --members jvan jvan
RUN_CHECK_CLIENT project-create --owner rwg --members rwg rwg
RUN_CHECK_CLIENT project-create --owner khurtado --members khurtado khurtado
RUN_CHECK_CLIENT project-create --owner sthapa --members sthapa sthapa
RUN_CHECK_CLIENT project-create --owner btovar --members btovar btovar

RUN_CHECK_CLIENT project-create --owner btovar --members lincolnb,jvan,rwg,khurtado,sthapa,btovar vc3-team

RUN_CHECK_CLIENT project-addallocation vc3-team btovar.ndccl
RUN_CHECK_CLIENT project-addallocation vc3-team khurtado.osg-connect
RUN_CHECK_CLIENT project-addallocation vc3-team lincolnb.uchicago-midway


