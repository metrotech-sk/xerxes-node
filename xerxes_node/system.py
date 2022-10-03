#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
import logging
import sys
from subprocess import TimeoutExpired
from threading import Lock
from threading import Thread
import time
from typing import List
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.network import ChecksumError, MessageIncomplete
from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from dataclasses import asdict
from rich import print

log = logging.getLogger(__name__)

class NetworkBusy(Exception):
    pass


class Duplex(Enum):
    HALF = 1
    FULL = 0


class XerxesSystem:
    def __init__(self, leaves: List[Leaf], mode: Duplex, root: XerxesRoot, std_timeout_s=-1):
        
        self._mode = mode
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self._leaves = leaves
        self._root = root
        self.measurements = {}

    def _poll(self):
        
        # if network is read/write exclusive:
        if self._mode == Duplex.HALF:
            lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
            if not lock_acq:
                log.warning("trying to access busy network")
                raise TimeoutExpired("unable to access network within timeout")

        # sync sensors 
        self._root.sync()
        time.sleep(0.2) # wait for sensors to acquire measurement

        for leaf in self._leaves:
            leaf: Leaf
            try:
                if not self.measurements.get(leaf):
                    self.measurements[leaf] = []
                self.measurements.get(leaf).append(leaf.fetch())
                
            except ChecksumError:
                log.warning(f"message from leaf {leaf.address} has invalid checksum")
            except MessageIncomplete:
                log.warning(f"message from leaf {leaf.address} is not complete.")
            except TimeoutError:
                log.warning(f"Leaf {leaf.address} is not responding.")
            # except Exception as e:
            #     tbk = sys.exc_info()[2]
            #     log.error(f"Unexpected error: {e}")    
            #     log.debug(tbk.tb_lineno)
                
        # release access lock
        if self._mode == Duplex.HALF:
            self._access_lock.release()

    def poll(self) -> None:
        if self._access_lock.locked() and self._mode == Duplex.HALF:
           raise NetworkBusy("Previous command is still in progress")
        poller = Thread(target = self._poll)
        poller.start()

    def busy(self) -> bool:
        return self._access_lock.locked()
        
    def wait(self, timeout=-1):
        locked = self._access_lock.acquire(timeout=timeout)
        self._access_lock.release()
        return locked
    
    def get_measurements(self):
        _m = self.measurements.copy()
        self.measurements = {}
        return _m