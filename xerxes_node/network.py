#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum
import logging
from subprocess import TimeoutExpired
from threading import Lock
from threading import Thread
from typing import List
from xerxes_node.hierarchy.branches.branch import Branch
from xerxes_node.hierarchy.leaves.leaf import ChecksumError, LengthError


class NetworkBusy(Exception):
    pass


class Duplex(Enum):
    HALF = 1
    FULL = 0


class XerxesNetwork:
    def __init__(self, branches: List[Branch], mode: Duplex, std_timeout_s=-1):
        self._branches = branches
        self._mode = mode
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self.log = logging.getLogger(__name__)

    def append_branch(self, branch: Branch):
        self._branches.append(branch)

    def _poll(self):
        # if network is read/write exclusive:
        if self._mode == Duplex.HALF:
            lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
            if not lock_acq:
                self.log.warning("trying to access busy network")
                raise TimeoutExpired("unable to access network within timeout")


        for branch in self._branches:
            for leaf in branch:
                try:
                    leaf.read()
                except LengthError:
                    self.log.warning(f"message from leaf {leaf.address} has invalid length")
                except ChecksumError:
                    self.log.warning(f"message from leaf {leaf.address} has invalid checksum")
                except TimeoutError:
                    self.log.warning(f"Leaf {leaf.address} is not responding.")
        
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
    
    @property
    def branches(self) -> List[Branch]:
        return list(self._branches)
    
    @branches.setter
    def branches(self, tmp):
        raise NotImplementedError