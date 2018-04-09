#!/bin/bash
#
# File:     sge_submit.sh
# Author:   Keith Sephton (kms@doc.ic.ac.uk)
#
# Based on pbs_submit.sh 
# Author:   David Rebatto (david.rebatto@mi.infn.it)
#
# Revision history:
#    xx-Apr-2008: Original release
#    11-Nov-2009: Mario David (david@lip.pt). Removed CELL information from $jobID
#
# Description:
#   Submission script for SGE, to be invoked by blahpd server.
#   Usage:
#     sge_submit.sh -c <command> [-i <stdin>] [-o <stdout>] [-e <stderr>] [-w working dir] [-- command's arguments]
#
# Copyright (c) Members of the EGEE Collaboration. 2004. 
# See http://www.eu-egee.org/partners/ for details on the copyright
# holders.  
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.
#

#exec 2>> /tmp/submit.log

. `dirname $0`/blah_common_submit_functions.sh

if [ -z "$sge_rootpath" ]; then sge_rootpath="/usr/local/sge/pro"; fi
if [ -r "$sge_rootpath/${sge_cellname:-default}/common/settings.sh" ]
then
  . $sge_rootpath/${sge_cellname:-default}/common/settings.sh
fi

bls_job_id_for_renewal=JOB_ID

original_args="$@"
bls_parse_submit_options "$@"

bls_setup_all_files

# Write wrapper preamble
cat > $bls_tmp_file << end_of_preamble
#!/bin/bash
#$ -cwd
# error = Merged with joblog
#$ -o joblog.$JOB_ID
#$ -j y
#$ -l h_rt=2:00:00,h_data=3G
end_of_preamble

# Email address to notify
#$ -M $USER@uchicago.edu
# Notify when
#$ -m bea

#local batch system-specific file output must be added to the submit file
local_submit_attributes_file=${GLITE_LOCATION:-/opt/glite}/bin/sge_local_submit_attributes.sh
if [ -r $local_submit_attributes_file ] ; then
    echo \#\!/bin/sh > $bls_opt_tmp_req_file
    if [ ! -z $bls_opt_req_file ] ; then
        cat $bls_opt_req_file >> $bls_opt_tmp_req_file
    fi
    echo "source $local_submit_attributes_file" >> $bls_opt_tmp_req_file
    chmod +x $bls_opt_tmp_req_file
    $bls_opt_tmp_req_file >> $bls_tmp_file 2> /dev/null
    rm -f $bls_opt_tmp_req_file
fi

if [ ! -z "$bls_opt_xtra_args" ] ; then
    echo -e $bls_opt_xtra_args >> $bls_tmp_file 2> /dev/null
fi

# Write SGE directives according to command line options
# handle queue overriding
[ -z "$bls_opt_queue" ] || grep -q "^#\$ -q" $bls_tmp_file || echo "#\$ -q $bls_opt_queue" >> $bls_tmp_file
[ -z "$bls_opt_mpinodes" -o "x${bls_opt_mpinodes}" = "x1" ] || grep -q"^#\$ -pe *\\*" $bls_tmp_file || echo "#\$ -pe * $bls_opt_mpinodes" >>$bls_tmp_file

# Input and output sandbox setup.
bls_fl_subst_and_accumulate inputsand "@@F_REMOTE@`hostname -f`:@@F_LOCAL" "@@@"
[ -z "$bls_fl_subst_and_accumulate_result" ] || echo "#\$ -v SGE_stagein=$bls_fl_subst_and_accumulate_result" >> $bls_tmp_file
bls_fl_subst_and_accumulate outputsand "@@F_REMOTE@`hostname -f`:@@F_LOCAL" "@@@"
[ -z "$bls_fl_subst_and_accumulate_result" ] || echo "#\$ -v SGE_stageout=$bls_fl_subst_and_accumulate_result" >> $bls_tmp_file

bls_add_job_wrapper

###############################################################
# Submit the script
###############################################################
#Your job 3236842 ("run") has been submitted
jobID=`qsub $bls_tmp_file 2> /dev/null | perl -ne 'print $1 if /^Your job (\d+) /;'` # actual submission
retcode=$?
if [ "$retcode" != "0" -o -z "$jobID" ] ; then
	rm -f $bls_tmp_file
	exit 1
fi
# 11/11/09 Mario David fix (remove CELL)
#jobID=$jobID.${SGE_CELL:-default}
TEMPDIR=$(mktemp -d)
cp $bls_tmp_file ${TEMPDIR}/.

# Compose the blahp jobID ("sge/" + datenow + sge jobid)
# 11/11/09 Mario David fix 
blahp_jobID=sge/`date +%Y%m%d%H%M%S`/$jobID

if [ "x$job_registry" != "x" ]; then
  now=`date +%s`
  let now=$now-1
  `dirname $0`/blah_job_registry_add "$blahp_jobID" "$jobID" 1 $now "$bls_opt_creamjobid" "$bls_proxy_local_file" "$bls_opt_proxyrenew_numeric" "$bls_opt_proxy_subject"
fi

echo "BLAHP_JOBID_PREFIX$blahp_jobID"
bls_wrap_up_submit

exit $retcode
