#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
import logging
import sys
from subprocess import TimeoutExpired
from threading import Lock
from threading import Thread
import time
from typing import List, Union
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
    _leaves = []

    def __init__(self, mode: Duplex, root: XerxesRoot, std_timeout_s=-1):
        
        self._mode = mode
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self._leaves = []
        self._root = root
        self._errors = 0
        self.measurements = {}


    def _poll(self):
        try:
            time_start_brut = time.perf_counter()
            # if network is read/write exclusive:
            if self._mode == Duplex.HALF:
                lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
                if not lock_acq:
                    log.warning("Trying to access busy network within timeout. Exitting.")
                    raise NetworkBusy("unable to access network within timeout")
        
            time_start_net = time.perf_counter()
            
            # sync sensors 
            self._root.sync()
            time.sleep(0.15) # wait for sensors to acquire measurement

            for leaf in self._leaves:
                leaf: Leaf
                if not self.measurements.get(leaf):
                    self.measurements[leaf] = []
                try:
                    time_leaf = time.perf_counter()
                    measurement = leaf.fetch()
                    self.measurements.get(leaf).append(measurement)
                    log.debug(f"Leaf: {leaf.address}, time: {time.perf_counter() - time_leaf}, {measurement}")
                except ChecksumError:
                    self._errors += 1
                    log.warning(f"message from leaf {leaf.address} has invalid checksum")
                except MessageIncomplete:
                    self._errors += 1
                    log.warning(f"message from leaf {leaf.address} is not complete.")
                except TimeoutError:
                    self._errors += 1
                    log.warning(f"Leaf {leaf.address} is not responding.")
                except Exception as e:
                    self._errors += 1
                    tbk = sys.exc_info()[:3]
                    log.error(f"Unexpected error: {e}")    
                    log.debug(tbk)
                    
            log.debug(f"sampled in {time.perf_counter() - time_start_brut}, net time: {time.perf_counter() - time_start_net}")

        finally:
            # release access lock
            if self._mode == Duplex.HALF:
                self._access_lock.release()


    def poll(self, blocking: bool=True) -> Union[None, Thread]:
        if blocking:
            self._poll()
        else:
            poller = Thread(target = self._poll)
            poller.start()
            return poller
        

    def wait(self, timeout=-1) -> bool:
        locked = self._access_lock.acquire(timeout=timeout)
        self._access_lock.release()
        return locked
    

    def get_measurements(self) -> dict:
        _m = self.measurements.copy()
        self.measurements = {}
        return _m


    def get_errors(self) -> int:
        e: int = self._errors
        self._errors = 0
        return e


    def discover(self, start: int=0, end: int=0xff) -> dict:
        result = dict()

        for i in range(start, end):
            a = Addr(i)
            l = Leaf(a, self._root)
            try:
                pr = l.ping()
                new_leaf = leaf_generator(l)
                if not new_leaf in self._leaves:
                    self._leaves.append(new_leaf)
                log.info(pr)
                log.info(new_leaf)
                result[str(int(l.address))] = pr.as_dict()
            except TimeoutError:
                pass
            except Exception as e:
                log.error(sys.exc_info()[:3])

        return result


