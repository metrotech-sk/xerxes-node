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
from xerxes_protocol.network import Addr
from xerxes_protocol.network import ChecksumError, MessageIncomplete
from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from xerxes_protocol.hierarchy.leaves.utils import leaf_generator
from dataclasses import asdict
from rich import print

log = logging.getLogger(__name__)

class NetworkBusy(Exception):
    pass


class Duplex(Enum):
    HALF = 1
    FULL = 0


class XerxesSystem:
    def __init__(self, mode: Duplex, root: XerxesRoot, std_timeout_s=-1):
        
        self._mode = mode
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self._leaves = []
        self._root = root
        self.measurements = {}

    def _poll(self):
        time_start_brut = time.monotonic()
        # if network is read/write exclusive:
        if self._mode == Duplex.HALF:
            lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
            if not lock_acq:
                log.warning("Trying to access busy network within timeout. Exitting.")
                raise NetworkBusy("unable to access network within timeout")
       
        time_start_net = time.monotonic()
        
        # sync sensors 
        self._root.sync()
        time.sleep(0.15) # wait for sensors to acquire measurement

        for leaf in self._leaves:
            if not self.measurements.get(leaf):
                self.measurements[leaf] = []
            try:
                time_leaf = time.monotonic()
                measurement = leaf.fetch()
                self.measurements.get(leaf).append(measurement)
                log.debug(f"Leaf: {leaf.address}, time: {time.monotonic() - time_leaf}, {measurement}")
            except ChecksumError:
                log.warning(f"message from leaf {leaf.address} has invalid checksum")
            except MessageIncomplete:
                log.warning(f"message from leaf {leaf.address} is not complete.")
            except TimeoutError:
                log.warning(f"Leaf {leaf.address} is not responding.")
            except Exception as e:
                tbk = sys.exc_info()[:3]
                log.error(f"Unexpected error: {e}")    
                log.debug(tbk)
                
        # release access lock
        if self._mode == Duplex.HALF:
            self._access_lock.release()
        log.debug(f"sampled in {time.monotonic() - time_start_brut}, net time: {time.monotonic() - time_start_net}")

    def poll(self) -> None:
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


    def discover(self, start: int=0, end: int=0xff):
        self._leaves = []
        result = dict()

        for i in range(start, end):
            a = Addr(i)
            l = Leaf(a, self._root)
            try:
                pr = l.ping()
                new_leaf = leaf_generator(l)
                self._leaves.append(new_leaf)
                log.info(pr)
                log.info(new_leaf)
                result[str(int(l.address))] = pr.as_dict()
            except TimeoutError:
                pass
            except Exception as e:
                log.error(sys.exc_info()[:3])

        return result


