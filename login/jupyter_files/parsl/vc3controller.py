#! /bin/env python3.6

from parsl.executors.ipp_controller import Controller

import random
import os
import logging
import subprocess

logger = logging.getLogger(__name__)

class VC3Controller(Controller):
    '''VC3 Controller for IPyParallel'''

    def __init__(self, public_ip=None, interfaces=None, port=None, port_range=None, reuse=False,
                 log=True, ipython_dir="~/.ipython", mode="auto", profile='default'):
        super().__init__(public_ip, interfaces, port, port_range, reuse,
                         log, ipython_dir, mode, profile)

        if self.port_range is not None:
            self.min_port, self.max_port = [int(i) for i in self.port_range.split(',')]
            (
              self.port,
              self.hb_low, self.hb_high,
              self.control_low, self.control_high,
              self.mux_low, self.mux_high,
              self.task_low, self.task_high
            ) = random.sample(range(self.min_port, self.max_port), 9)

    def start(self):
        """Start the controller."""

        if self.mode == "manual":
            return

        if self.ipython_dir is not '~/.ipython':
            self.ipython_dir = os.path.abspath(os.path.expanduser(self.ipython_dir))

        if self.log:
            stdout = open(os.path.join(self.ipython_dir, "{0}.controller.out".format(self.profile)), 'w')
            stderr = open(os.path.join(self.ipython_dir, "{0}.controller.err".format(self.profile)), 'w')
        else:
            stdout = open(os.devnull, 'w')
            stderr = open(os.devnull, 'w')

        try:
            opts = [
                'ipcontroller',
                '' if self.ipython_dir is '~/.ipython' else '--ipython-dir={}'.format(self.ipython_dir),
                self.interfaces if self.interfaces is not None else '--ip=*',
                '' if self.profile is 'default' else '--profile={0}'.format(self.profile),
                '--reuse' if self.reuse else '',
                '--port={}'.format(self.port) if self.port is not None else '',
                '--location={}'.format(self.public_ip) if self.public_ip else '',
                '--HubFactory.hb={0},{1}'.format(self.hb_low, self.hb_high),
                '--HubFactory.control={0},{1}'.format(self.control_low, self.control_high),
                '--HubFactory.mux={0},{1}'.format(self.mux_low, self.mux_high),
                '--HubFactory.task={0},{1}'.format(self.task_low, self.task_high),

            ]
            logger.debug("Starting ipcontroller with '{}'".format(' '.join([str(x) for x in opts])))
            self.proc = subprocess.Popen(opts, stdout=stdout, stderr=stderr, preexec_fn=os.setsid)
        except FileNotFoundError as e:
            msg = "Could not find ipcontroller. Please make sure that ipyparallel is installed and available in your env"
            logger.error(msg)
            raise ControllerError(msg)
        except Exception as e:
            msg = "IPPController failed to start: {0}".format(e)
            logger.error(msg)
            raise ControllerError(msg)
