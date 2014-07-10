END-USER CONDOR GLIDEIN WRAPPER
John Hover <jhover@bnl.gov>
===============================

Since it seems the old condor_glidein has been deprecated, we need a simple mechanism to submit glideins. This single-file Python wrapper allows full configuration via command-line switches, and supports GSI auth. So all input values can safely be put into a condor submit file and the wrapper submitted to a grid resource. 

INSTALLATION
Since it is a single file, it can be submitted directly from an SVN checkout dir. Or it can be built as an RPM ('python setup.py bdist__rpm') and submitted from the Python lib area. 

USAGE
Wrapper downloads Condor via HTTP, unpacks Condor, sets up configuration files, and runs condor_master. The glidein job will stay at least <lingertime> seconds, run at most one job, and then exit. 

A sample Condor submit file is included for submission to a CE. The DN of the submitter must be added to the collector and schedd grid-mapfiles as mapping to condor_pool. 

The script downloads the official Condor tarball from somewhere they have been posted. It assumes the name of the tarball is the default from the Condor team. The host and path can be arbitrary, though. 

The script can be run directly on a host, as long as you pre-set X509_USER_PROXY env var pointing to a valid proxy file (i.e. one allowed on the central manager). 

Required args:
-c <collector-hostname>
-p <collector-port>
-a <gsi|password>
-t <password | DN list>

Note that the DN list needs to be comma-separated and quoted. Check glidein job output if you have problems. The condor submit file example uses new-style args syntax to make the quoting work properly. 


LIMITATIONS
-- Assumes target WN:
  Is Redhat 6 or derivative
  Is x86_64 architecture
  Has Python
  Has the UNIX 'file', and 'tar' commands. 

-- By default downloads are from dev.racf.bnl.gov, where I only have condor 8.0.6 and  8.1.3. Since the path is also an arg, a user can set up whatever versions and archs they might want. 

-- Currently limited to very basic functionality. START=TRUE for the startd and there is no way to inject ClassAds yet.

-- Assumes CA cert dir is /etc/grid-security/certificates. It didn't seem to be set as an arbirary env var on our cluster. 


FILES

/etc/grid-security/grid-mapfile   ON collector and schedd
"/DC=com/DC=DigiCert-Grid/O=Open Science Grid/OU=People/CN=John Hover 241/CN=proxy" condor_pool
"/DC=com/DC=DigiCert-Grid/O=Open Science Grid/OU=People/CN=John Hover 241" condor_pool









  