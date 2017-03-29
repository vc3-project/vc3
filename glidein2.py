#!/bin/env python

import optparse
import urllib
import platform
import os
import errno
import sys
import logging
import tempfile
import shutil
import tarfile
import signal
import subprocess
import textwrap

class CondorGlidein(object):

    def __init__(self, 
                    condor_version="8.6.0",
                    condor_urlbase="http://download.virtualclusters.org/repository",
                    collector="condor.grid.uchicago.edu:9618",
                    lingertime=600,
                    loglevel=logging.DEBUG,
                    workdir=None,
                    noclean=False
                ):
        self.condor_version = condor_version
        self.condor_urlbase = condor_urlbase
        self.collector = collector
        self.lingertime = lingertime
        self.loglevel = loglevel
        self.noclean = noclean

        # Other items that are set later
        #self.condor_platform = None # condor-version-arch_distro-stripped
        #self.condor_tarball = None # the above w/ .tar.gz added
        #self.iwd = None # initial working directory for the glidein extraction 
        #self.glidein_dir = None # iwd + glidein dir name
        #self.log = None  # logging
        #self.injector_path = None # injector for extra classads
        #self.exec_wrapper = None
        #self.startd_cron = None
        

        self.setup_signaling()
        self.setup_logging(loglevel)
        self.download_tarball()
        self.setup_workdir(workdir)
        self.unpack_tarball()
        #self.write_injector()
        self.initial_config()
        if noclean is False:
            self.cleanup()

    def setup_signaling(self):
        """
        Interrupt handling to trigger the cleanup function whenever Ctrl-C
        or something like `kill` is sent to the process
        """
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def setup_logging(self, loglevel):
        """
        Setup the logging handler and format
        """
        formatstr = "[%(levelname)s] %(asctime)s %(module)s.%(funcName)s(): %(message)s"
        self.log = logging.getLogger()
        hdlr = logging.StreamHandler(sys.stdout) 
        formatter = logging.Formatter(formatstr)
        hdlr.setFormatter(formatter)
        self.log.addHandler(hdlr)
        self.log.setLevel(loglevel)
        
    def setup_workdir(self, path = None):
        """ 
        Setup the working directory for the HTCondor binaries, configs, etc. 
        
        If no argument is passed, then generate a random one in the current
        working directory. Otherwise use the path specified
        """
        if path is None:
            self.iwd = os.getcwd()
        else:
            self.iwd = path

        try:
            self.glidein_dir = tempfile.mkdtemp(prefix="%s/condor-glidein." % self.iwd)
            self.log.info("Glidein working directory is %s" % self.glidein_dir)
        except Exception as e:
            self.log.debug(e)
            self.log.error("Failed to create working directory")
            self.cleanup()

    def download_tarball(self):
        """
        Determine the worker's architecture and distribution, download the 
        appropriate release of HTCondor. 
        """
    
        if platform.machine() == 'x86_64':
            arch = platform.machine()
        else:
            self.log.error("Only x86_64 architecture is supported")
            raise Exception

        condor_version = self.condor_version

        distro_name = platform.linux_distribution()[0]
        distro_major = platform.linux_distribution()[1].split(".",1)[0]
         
        if platform.system() == 'Linux':
            if "Scientific" or "CentOS" or "Red Hat" in distro_name:
                distro = "RedHat" + distro_major
            elif "Debian" in distro_name:
                distro = "Debian" + distro_major
            elif "Ubuntu" in distro_name:
                distro = "Ubuntu" + distro_major
            else:
                raise Exception("Unable to determine distro")
        elif platform.system() == 'Darwin':
                distro = 'MacOSX' # why not?

        self.condor_platform = "condor-%s-%s_%s-stripped" % (condor_version,
                                                        arch, distro)

        tarball_name = self.condor_platform + ".tar.gz"

        src = self.condor_urlbase + "/" + tarball_name

        self.condor_tarball = os.getcwd() + "/" + tarball_name

        self.log.info("Downloading HTCondor tarball")
        self.log.debug("%s > %s", src, self.condor_tarball)

        try:
            urllib.urlretrieve(src, self.condor_tarball) 
        except Exception as e:
            self.log.debug(e)
            self.log.error("Failed to retrieve the tarball")
            self.cleanup()

        cmd = "file %s" % self.condor_tarball
        out = self.runcommand(cmd)
        if "gzip compressed data" in out:
            self.log.debug("Filetype is gzip")
        else:
            self.log.error("File type is incorrect. Aborting.")
            self.cleanup()

    def unpack_tarball(self):
        """
        Unpack the HTCondor tarball to glidein_dir
        """
        try:
            tar = tarfile.open(self.condor_tarball)
            tar.extractall(path=self.glidein_dir + '/')
            tar.close()
            os.remove(self.condor_tarball)
        except Exception as e:
            self.log.debug(e)
            self.log.error("Failed to unpack the tarball")
            self.cleanup()
        
    def cleanup(self):
        """
        Remove any files that may have been created at glidein start time

        Some operations are not atomic, e.g., deleting the tarball after
        extracting it. Make sure we clean this up!
        """ 
        if self.noclean is True:
            self.log.info("'No Clean' is true -- exiting without cleaning up!")
            sys.exit(1)

        self.log.info("Removing working directory and leftover files")

        try:
            os.remove(self.condor_tarball)
        except OSError as e:
            if e.errno == errno.ENOENT:
                self.log.debug("Tarball already cleaned up.")
            else:
                self.log.warn("Tarball exists but can't be removed for some reason")
            pass

        try:
            shutil.rmtree(self.glidein_dir)
        except AttributeError:
            self.log.debug("Working directory is not yet defined -- ignoring")
            pass
        except:
            self.log.warn("Failed to remove %s !" % self.glidein_dir)
            pass
        sys.exit(1)

    def initial_config(self):
        """
        Write out a basic HTCondor config to <glidein_dir>/etc/condor/00.conf

        This configuration can later be overwritten by a startd cron that
        checks for additional config.
        """
        config_bits = []

        dynamic_config = """ 
            COLLECTOR_HOST = %s
            STARTD_NOCLAIM_SHUTDOWN = %s
            START = %s
            STARTD_CRON_injector_EXECUTABLE = %s
        """ % (self.collector, self.lingertime, "TRUE", self.injector_path)

        config_bits.append(dynamic_config)

        static_config = """
            SUSPEND                     = FALSE
            PREEMPT                     = FALSE
            KILL                        = FALSE
            RANK                        = 0
            CLAIM_WORKLIFE              = 3600
            JOB_RENICE_INCREMENT        = 0
            HIGHPORT                    = 30000
            LOWPORT                     = 20000
            DAEMON_LIST                 = MASTER, STARTD 
            ALLOW_WRITE                 = condor_pool@*, submit-side@matchsession
            SEC_DEFAULT_AUTHENTICATION  = REQUIRED
            SEC_DEFAULT_ENCRYPTION      = REQUIRED
            SEC_DEFAULT_INTEGRITY       = REQUIRED
            ALLOW_ADMINISTRATOR         = condor_pool@*/*
        """

        config_bits.append(static_config)

        if self.exec_wrapper:
            wrapper = "USER_JOB_WRAPPER = %s" % (self.exec_wrapper)
            config_bits.append(wrapper)
        
        if self.startd_cron:
            cron = """
                STARTD_CRON_JOBLIST          = generic
                STARTD_CRON_generic_PERIOD   = 5m
                STARTD_CRON_generic_MODE     = PERIODIC
                STARTD_CRON_generic_RECONFIG = TRUE
                STARTD_CRON_generic_KILL     = TRUE
                STARTD_CRON_generic_ARGS     = NONE 
            """
            config_bits.append(cron)

        config = textwrap.dedent("".join(config_bits))
        config_path = self.glidein_dir + "/etc/condor/glidein.conf"

        self.log.debug("Configuration built: %s " % config)
            
        
        try:
            target = open(config_path, 'w')
            target.write(config)
            target.close()
            self.log.debug("Wrote %s" % config_path)
        except Exception as e:
            self.log.error("Unable to write config %s" % config_path)
            self.log.debug(e)
            self.cleanup()

    #
    # Utilities
    #

    def interrupt_handler(self, signal, frame):
        """
        Simply catches signals and runs the cleanup script
        """
        self.log.info("Caught signal, running cleanup")
        self.cleanup()
        sys.exit(1)

    def runcommand(self, cmd):
        """
        Helpful little function to run external *nix commands
        """
        self.log.debug("cmd = %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        out = out.rstrip()
        if p.returncode == 0:
            self.log.debug("External command output: %s" % out)
        else:
            self.log.error("External command failed: %s" % err)
            self.cleanup()
        return out
            

if __name__ == '__main__':
    gi = CondorGlidein() 
