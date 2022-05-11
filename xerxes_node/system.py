#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from subprocess import TimeoutExpired
from threading import Lock
from threading import Thread
from xerxes_node.leaves.pleaf import PLeaf


class NetworkBusy(Exception):
    pass


class XerxesSystem:
    def __init__(self, leaves: list, exclusive_communication=True, std_timeout_s=-1):
        self._leaves = leaves
        self._exclusive_communication = exclusive_communication
        self._access_lock = Lock()
        self._std_timeout_s = std_timeout_s
        self._readings = []
        self.log = logging.getLogger(__name__)


    def _poll(self):
        # if network is read/write exclusive:
        if self._exclusive_communication:
            lock_acq = self._access_lock.acquire(blocking=True, timeout=self._std_timeout_s)
            if not lock_acq:
                self.log.warning("trying to access busy network")
                raise TimeoutExpired("unable to access network within timeout")

        network_snap = {}
        for i in range(len(self._leaves)):
            leaf = self._leaves[i]
            try:
                leaf_reading = leaf.read()
                network_snap[leaf.address] = leaf_reading
            except IOError:
                self.log.warning(f"message from leaf {leaf.address} is corrupted")
            except TimeoutError:
                self.log.warning(f"Leaf {leaf.address} is not responding.")
        
        self._readings.append(network_snap)

        # release access lock
        if self._exclusive_communication:
            self._access_lock.release()


    def poll(self):
        if self._access_lock.locked() and self._exclusive_communication:
           raise NetworkBusy("Previous command is still in progress")
        poller = Thread(target = self._poll)
        poller.start()


    def busy(self):
        return self._access_lock.locked()
        

    def wait(self, timeout=-1):
        locked = self._access_lock.acquire(timeout=timeout)
        self._access_lock.release()
        return locked


    def get(self):
        # reset counter
        readings = list(self._readings)
        self._readings = []
        return readings
    

    def average(self, flush=True):
        "return the average of aggregated results"
        averages = dict()
        for leaf in self._leaves:
            addr = leaf.addr
            leaf_vals = []
            for reading in self._readings:
                leaf_vals.append(reading.get(addr))

            try:    
                averages[addr] = PLeaf.average(leaf_vals)
            except ValueError:
                averages[addr] = None
        
        if flush:
            self._readings=[]

        return averages

