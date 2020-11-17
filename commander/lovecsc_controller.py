"""The LOVE CSC."""
import argparse
import asyncio
import sys
import warnings
from lsst.ts import salobj

HEARTBEAT_INTERVAL = 1  # seconds

class LOVECsc(salobj.Controller):
    """
    Define the LOVE CSC as a SAL CSC 
    """

    def __init__(self):
        super().__init__(name="LOVE", index=None, do_callbacks=False)

    #     self.heartbeat_interval = HEARTBEAT_INTERVAL

    def add_observing_log(self, user, message):
        """Add message to observing log

        Parameters
        ----------
        user: string
            The name of the user who sent the observing log
        message: string
            The observing log
        """
        self.evt_observingLog.set(user=user, message=message)
        self.evt_observingLog.put()
