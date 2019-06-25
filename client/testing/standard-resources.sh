#!/bin/bash

source ./standard-common-config.sh

# Generic node size:
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Generic node size, 1core,1GB,1GB" --cores 4 --memory_mb 1000 --storage_mb 1000 generic-nodesize

# Create resource midway
RUN_CHECK_CLIENT nodeinfo-create --owner lincolnb  --displayname="Node size for uchicago-midway (amd partition)" --cores 1 --memory_mb 1900 --storage_mb 10000 --native_os "scientificlinux:v6.7" uchicago-midway-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost midway-login1.rcc.uchicago.edu --accessport 22 --node uchicago-midway-nodesize --description "Midway 1 cluster at the University of Chicago Research Computing Center (RCC)" --displayname "Midway 1" --url "https://rcc.uchicago.edu/" --docurl "https://rcc.uchicago.edu/docs/" --organization "University of Chicago - Research Computing Center (RCC)" uchicago-midway --public

# Create resource Syracuse
RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor condor --accesshost its-condor-submit.syr.edu --accessport 22 --node generic-nodesize --description "Syracuse OrangeGrid" --displayname "OrangeGrid"  --url "http://researchcomputing.syr.edu/resources/orange-grid/" --docurl "http://researchcomputing.syr.edu/orangegrid-intro/" --organization "Syracuse University" syr-orangegrid


# Create resource CoreOS
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Generic node size, 1core,1GB,1GB" --cores 4 --memory_mb 1000 --storage_mb 1000 --native_os "scientificlinux:v6.9" --features singularity coreos-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch  --accessmethod ssh  --accessflavor condor  --accesshost condor.grid.uchicago.edu --accessport 22 --node coreos-nodesize --description "CoreOS/Kubernetes Cluster with HTCondor Overlay"  --displayname "CoreOS"  --url ""  --docurl ""  --organization "University of Chicago" uchicago-coreos --public


# Create resource VC3 test pool
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Generic node size, 1core,1GB,1GB" --cores 4 --memory_mb 1000 --storage_mb 1000 --native_os "centos:v6.9" vc3testpool-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb  --accesstype batch --accessmethod ssh --accessflavor condor --accesshost pool.virtualclusters.org  --accessport 22 --node vc3testpool-nodesize --description "VC3 Public Test Pool" --displayname "VC3 Test"  --url "http://www.virtualclusters.org/"  --docurl "https://github.com/vc3-project/vc3-user-guide/blob/master/userguide.md" --organization "VC3"  vc3-test-pool --public


# Create resource NERSC Cori
RUN_CHECK_CLIENT nodeinfo-create --owner lincolnb  --displayname="Node size for nersc-cori (Haswell partition)" --cores 32 --memory_mb 3775 --storage_mb 10000 --native_os "suse:v12" --features shifter nersc-cori-nodesize

RUN_CHECK_CLIENT resource-create  --owner lincolnb  --accesstype batch  --accessmethod ssh --accessflavor slurm   --accesshost cori.nersc.gov  --accessport 22 --node nersc-cori-nodesize --description "Cori Supercomputer at NERSC" --displayname "Cori"  --url "https://www.nersc.gov/users/computational-systems/cori/"  --docurl "http://www.nersc.gov/users/computational-systems/cori/getting-started/" --pubtokendocurl "http://www.nersc.gov/users/connecting-to-nersc/connecting-with-ssh/#toc-anchor-2" --organization "National Energy Research Scientific Computing Center (NERSC)" nersc-cori --public


# Create resource uct2-gk
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Generic node size, 1core,1GB,1GB" --cores 4 --memory_mb 1900 --storage_mb 1000 --native_os "scientificlinux:v6.9" uct2gk-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch  --accessmethod ssh  --accessflavor condor  --accesshost uct2-gk.mwt2.org --accessport 22 --node uct2gk-nodesize --description "ATLAS Midwest Tier 2 Center Job Gateway at UChicago"  --displayname "MWT2" --url "http://twiki.mwt2.org"  --docurl "http://twiki.mwt2.org"  --organization "Midwest Tier 2" uchicago-mwt2 --public

# Create resource uct3-s1
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Generic node size, 1core,1GB,1GB" --cores 4 --memory_mb 1900 --storage_mb 1000 --native_os "scientificlinux:v6.9" uct3s1-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch  --accessmethod ssh  --accessflavor condor  --accesshost uct3-s1.mwt2.org --accessport 22 --node uct3s1-nodesize --description "UChicago ATLAS Tier 3"  --displayname "UCT3" --url "https://hep.uchicago.edu/atlas/"  --docurl "http://twiki.mwt2.org"  --organization "University of Chicago - Enrico Fermi Institute" uchicago-uct3 --public


# Create resource TACC Stampede
RUN_CHECK_CLIENT nodeinfo-create --owner lincolnb  --displayname="Node size for tacc-stampede2 (SKX partition)" --cores 96 --memory_mb 2000 --storage_mb 10000 --native_os "centos:v7.4" --features singularity tacc-stampede2-nodesize

RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch --accessmethod ssh  --accessflavor slurm --accesshost login5.stampede2.tacc.utexas.edu --accessport 22 --node tacc-stampede2-nodesize --description "Stampede2 Super Computer"  --displayname "Stampede2" --url "https://www.tacc.utexas.edu/"  --docurl "https://portal.tacc.utexas.edu/user-guides/stampede2"  --organization "Texas Advanced Computing Center (TACC)" tacc-stampede2 --public


# Create resource ND CCL
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Node size for ndccl" --cores 4 --memory_mb 2200 --storage_mb 10000 --native_os "redhat:v7" --features singularity ndccl-nodesize

RUN_CHECK_CLIENT resource-create --owner btovar --accesstype batch --accessmethod ssh --accessflavor condor --accesshost cclvm05.crc.nd.edu --accessport 22 --node ndccl-nodesize --description "Notre Dame CCL Job Gateway" --displayname "ND CCL" --url "https://ccl.cse.nd.edu/" --docurl "https://ccl.cse.nd.edu/" --organization "University of Notre Dame Cooperative Computing Lab (CCL)" ndccl --public


# Create resource UCLA Hoffman2
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Node size for ucla-hoffman2" --cores 8 --memory_mb 2750 --storage_mb 10000 --native_os "centos:v6.9" ucla-hoffman2-nodesize

RUN_CHECK_CLIENT resource-create --owner briedel --accesstype batch --accessmethod ssh --accessflavor sge --accesshost login1.hoffman2.idre.ucla.edu --accessport 22 --node ucla-hoffman2-nodesize --description "UCLA Hoffman2 Cluster" --displayname "Hoffman2" --url "https://idre.ucla.edu/resources/hpc/hoffman2-cluster" --organization "University of California,  Los Angeles" ucla-hoffman2 --public


# Create resource osgconnect
RUN_CHECK_CLIENT resource-create --owner lincolnb --accesstype batch --accessmethod ssh --accessflavor condor --accesshost vc3-gateway.osgconnect.net --accessport 22 --node generic-nodesize --description "Open Science Grid" --displayname "OSG Connect" --url "https://support.opensciencegrid.org" --pubtokendocurl "https://support.opensciencegrid.org/support/solutions/articles/12000027675-generate-ssh-key-pair-and-add-the-public-key-to-your-account#step-2-add-the-public-ssh-key-to-login-node" --organization "Open Science Grid" osg-connect --public

# Create resource cmsconnect
RUN_CHECK_CLIENT nodeinfo-create --owner khurtado --displayname="Node size for CMS Connect" --cores 2 --memory_mb 3800 --storage_mb 7000 cmsconnect-nodesize

RUN_CHECK_CLIENT resource-create --owner khurtado --accesstype batch --accessmethod ssh --accessflavor condor --accesshost login.uscms.org --accessport 22 --node cmsconnect-nodesize --description "CMS Connect" --displayname "CMS Connect" --url "http://docs.uscms.org" --pubtokendocurl "http://docs.uscms.org/Generate+SSH+key+pair+and+add+the+public+key+to+your+account" --organization "CMS" cms-connect --public

# Create resource bridges
RUN_CHECK_CLIENT nodeinfo-create --owner btovar  --displayname="Node size for psc-bridges (RMS partition)" --cores 28 --memory_mb 4000 --storage_mb 35000 --native_os "centos:v7.3"  --features singularity psc-bridges-nodesize

RUN_CHECK_CLIENT resource-create --owner khurtado --accesstype batch --accessmethod ssh --accessflavor slurm --accesshost bridges.psc.edu --accessport 22 --node psc-bridges-nodesize --description "Bridges Supercomputer at PSC" --displayname "Bridges" --url "https://www.psc.edu/bridges/" --docurl "https://www.psc.edu/bridges/user-guide/running-jobs" --pubtokendocurl "https://www.psc.edu/bridges/user-guide/connecting-to-bridges#keys" --organization "Pittsburgh Supercomputing Center" psc-bridges --public

# Create resource Blue Waters
RUN_CHECK_CLIENT nodeinfo-create --owner khurtado  --displayname="Node size for bluewaters-ncsa" --cores 1 --memory_mb 2000 --storage_mb 4000 --native_os "suse:v12" --features shifter bluewaters-ncsa-nodesize

RUN_CHECK_CLIENT resource-create --owner khurtado --accesstype batch --accessmethod gsissh --accessflavor pbs --accesshost h2ologin.ncsa.illinois.edu --accessport 22 --node bluewaters-ncsa-nodesize --description "Blue Waters petascale supercomputer" --displayname "Blue Waters" --url "https://bluewaters.ncsa.illinois.edu" --docurl "https://bluewaters.ncsa.illinois.edu/batch-jobs" --organization "Blue Waters NCSA" bluewaters-ncsa --public
