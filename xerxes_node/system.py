#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import tempfile
from threading import Thread, Lock
import time
from typing import (
    Dict, 
    List
)
from xerxes_protocol import (
    XerxesRoot,
    ChecksumError, 
    MessageIncomplete,
    Leaf
)
import pickle


log = logging.getLogger(__name__)


def add_timestamp(data: Dict) -> None:
    """Add timestamp to data dict."""
    
    data.update(
        {    
            "time":{
                "epoch": time.time(),
                "gm_time": time.asctime(time.gmtime()),
            }   
        }
    )
    

class XerxesSystem:
    
    threadpool = []
    measurements = {}
    measurements_lock = Lock()
    
    def __init__(self, roots: List[XerxesRoot], sample_period: float, syncing = False):
        self.roots = roots
        self._errors = 0
        self._syncing = syncing
        self._sample_period = sample_period

    def _poll(self, root: XerxesRoot):
        while self._run:
            time_start_us = time.perf_counter()

            for leaf in root.leaves:
                # get data from every leaf
                
                leaf: Leaf
                process_values: dict = leaf.process_values
                label = leaf.label
                
                self.measurements_lock.acquire()
                
                # these are in format {'pressure': 'pv0', 'temperature': 'pv3'} 
                if not self.measurements.get(label):
                    # create entry for this leaf
                    self.measurements[label] = {}
                    
                    for key, value in process_values.items():
                        self.measurements[label].update({key: []})
                
                try:
                    # now we have a dict with keys like pressure and temperature
                    # and empty lists as values
                    for key, value in process_values.items():
                        # this will read the value from the leaf
                        pv = leaf.__getattribute__(value)  
                        self.measurements.get(label).get(key).append(pv)
                        log.debug(
                            f"Leaf: {leaf.address}, key: {key}, value: {value}, pv: {pv}"
                        )
                        
                except ChecksumError:
                    self._errors += 1
                    log.warning(f"message from leaf {leaf.address} has invalid checksum")
                    
                except MessageIncomplete:
                    self._errors += 1
                    log.warning(f"message from leaf {leaf.address} is not complete.")
                    
                except TimeoutError:
                    self._errors += 1
                    log.warning(f"Leaf {leaf.address} is not responding.")

                except ValueError:
                    self._errors += 1
                    log.warning(f"Leaf {leaf.address} returned empty data.")
                    
                except Exception as e:
                    self._errors += 1
                    traceback = sys.exc_info()[:3]
                    log.error(f"Unexpected error: {e}, Traceback:\n{traceback}")
                
                self.measurements_lock.release()
                    
            cycletime_s = (time.perf_counter() - time_start_us)
            log.debug(f"sampled in {(cycletime_s) * 1000} ms")
            
            # sleep for the rest of the sample period
            sleep_for_s = self._sample_period - cycletime_s
            if sleep_for_s > 0:
                time.sleep(sleep_for_s)
            else:
                log.warning(
                    f"Sampling period of {self._sample_period} s exceeded by {sleep_for_s * -1} s."
                )
                

    def spin(self) -> None:
        self._run = True
        for _xr in self.roots:
            _t = Thread(
                target=self._poll, 
                args=(_xr,),
                name = f"XerxesSystem-{str(_xr.network._s.port)}"
            ) 
            _t.start()
            self.threadpool.append(_t)
    
    
    def status(self) -> Dict:
        status = {}
        for thread in self.threadpool:
            status.update(
                {
                    thread.name: thread.is_alive(),
                }
            )
        return status
            
    
    def stop(self) -> None:
        self._run = False
        for thread in self.threadpool:
            thread.join()
    
            
    def _average_measurements(self, data: Dict) -> None:
        log.debug(
            f"Before averaging: {data}"
        )
        for label, values in data.items():
            for process_value, value_array in values.items():
                try:
                    data[label][process_value] = sum(value_array) / len(value_array)
                except ZeroDivisionError:
                    # delete empty lists
                    data[label][process_value] = None
        log.debug(
            f"After averaging: {data}"
        )
        return data
        
    
    def dump(self, directory: str) -> None:
        # lock so we do not corrupt measurements or the pollers won't interfere
        # with data averaging
        self.measurements_lock.acquire()
        data = dict(self.measurements)
        # clean up the old data
        self.measurements = {}
        # dont forget to release the lock
        self.measurements_lock.release()
        
        data = {
            "measurements": self._average_measurements(data)
        }
        
        add_timestamp(data)
        
        # dump to file for later processing
        tf = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".dat",
            prefix="meas",
            dir=directory
        )
        pickle.dump(
            obj=data,
            file=tf
        )
        tf.close()
        
        