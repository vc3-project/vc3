#!/bin/bash

echo
echo "################################################################################"
echo "#####                                                                      #####"
echo "#####        Job is running within a Remote Cluster Connect Factory        #####"
echo "#####                                                                      #####"
echo "##### Date: $(echo $(date)         | sed -e :a -e 's/^.\{1,60\}$/& /;ta')  #####"
echo "##### RCCF: $(echo '<%= bosco_factory %>' | sed -e :a -e 's/^.\{1,60\}$/& /;ta')  #####"
echo "##### User: $(echo $(whoami)       | sed -e :a -e 's/^.\{1,60\}$/& /;ta')  #####"
echo "##### Host: $(echo $(hostname)     | sed -e :a -e 's/^.\{1,60\}$/& /;ta')  #####"
echo "#####                                                                      #####"
echo "################################################################################"
echo

######################################################################################

# Setup $PATH if none is defined
[[ -z "${PATH}" ]] && export PATH="/usr/bin:/bin:/usr/sbin:/sbin"

# Setup $HOME since many applications look for it
[[ -z "${HOME}" ]] && export HOME="${_CONDOR_JOB_IWD}"



# Cluster information that would match the "Requirements"
export IS_RCC="True"
export IS_RCC_<%= bosco_factory %>="True"

# Internal information a job might want to know
export _RCC_Factory="<%= bosco_factory %>"
export _RCC_Port="<%= bosco_port %>"
export _RCC_IterationTime="<%= bosco_iterationtime %>"
export _RCC_MaxIdleGlideins="<%= bosco_maxidleglideins %>"
export _RCC_MaxQueuedJobs="<%= bosco_maxqueuedjobs %>"
export _RCC_MaxHeldJobs="<%= bosco_maxheldjobs %>"
export _RCC_MaxRunningJobs="<%= bosco_maxrunningjobs %>"
export _RCC_JobProbeInterval="<%= bosco_jobprobeinterval %>"
export _RCC_JobProbeRate="<%= bosco_jobproberate %>"
export _RCC_MaxSlotLife="<%= bosco_maxslotlife %>"
export _RCC_MinSlotLife="<%= bosco_minslotlife %>"
export _RCC_MinSlotNoClaim="<%= bosco_minslotnoclaim %>"
export _RCC_NumCpusPerGlidein="<%= bosco_numcpusperglidein %>"
export _RCC_NumCpusPerSlot="<%= bosco_numcpusperslot %>"
export _RCC_NumSlots="<%= bosco_numslots %>"
export _RCC_ConnectScratch="<%= bosco_connectscratch %>"
export _RCC_FrontierServerURL="<%= bosco_frontierserverurl %>"
export _RCC_FrontierProxyURL="<%= bosco_frontierproxyurl %>"
export _RCC_HTTPProxy="<%= bosco_httpproxy %>"
export _RCC_ParrotProxy="<%= bosco_parrotproxy %>"
export _RCC_CVMFS="<%= bosco_cvmfs %>"
export _RCC_CVMFSProxy="<%= bosco_cvmfsproxy %>"
export _RCC_CVMFSMount="<%= bosco_cvmfsmount %>"
export _RCC_CVMFSScratch="<%= bosco_cvmfsscratch %>"
export _RCC_CVMFSQuota="<%= bosco_cvmfsquota %>"
export _RCC_OSG_APP="<%= bosco_osg_app %>"
export _RCC_OSG_GRID="<%= bosco_osg_grid %>"
export _RCC_UseTBace="<%= bosco_usetbace %>"
export _RCC_Scratch="<%= bosco_scratch %>"
export _RCC_BoscoVersion="<%= bosco_version %>"


# Make XrootD map properly for UChicago
#export XrdSecGSISRVNAMES=*



# If we find a local copy of the connect_wrapper, use it
# Other we will run the job as a *native*

if [[ -f "${_condor_LOCAL_DIR}/connect/connect_wrapper.sh" ]]; then
  ${_condor_LOCAL_DIR}/connect/connect_wrapper.sh "$@"
  wrapperRet=$?  
else
  ${_condor_LOCAL_DIR}/exec_wrapper.sh "$@"
  wrapperRet=$?
fi


echo
echo "################################################################################"
echo "################################ Job Complete ##################################"
echo "################################################################################"

exit ${wrapperRet}
