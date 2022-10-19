#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from rich import print
import os
import time
import socket
import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from xerxes_protocol.network import XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
import xerxes_node.config as config
from xerxes_node.system import Duplex, XerxesSystem
from xerxes_node.utils import get_cpu_temp_celsius
from multiprocessing import Manager
from threading import Thread

from flask import Flask

app = Flask(__name__)


file_path = os.path.realpath(__file__)
script_dir = os.path.dirname(file_path)

import os, time


HOSTNAME = socket.gethostname()

data = dict()


def home_dir(path):
    return os.path.join(os.path.expanduser("~"), path)


def timestamp(data: dict) -> dict:
    data.update({    
        "time":{
            "epoch": time.time(),
            "gm_time": time.asctime(time.gmtime()),
        }   
    })


class Runner(Thread):
    def __init__(
            self, 
            collection: Collection, 
            system: XerxesSystem, 
            sample_period: float, 
            log_period: float, 
            daemon: bool = False
        ):

        self.colelction = collection            
        self.system = system
        self.sample_period = sample_period
        self.log_period = log_period
        super().__init__(daemon=daemon)


    def run(self):

        current_period = self.log_period
        last_cycle = time.perf_counter()
        run_count = 1

        while True:
            while not self.system.wait(1):
                log.info("Xerxes system is busy...")
            self.system.poll()

            cycletime = time.perf_counter() - last_cycle
            try:
                time.sleep(self.sample_period-cycletime)
                log.debug(f"Cycletime: {cycletime}, sleeping for {self.sample_period-cycletime}.")
            except ValueError:
                log.warning(f"Cycle time {cycletime} is longer than sample period {self.sample_period}")

            if self.sample_period > cycletime:
                current_period += self.sample_period
            else:
                current_period += cycletime
            last_cycle = time.perf_counter()
            
            if current_period >= self.log_period:
                current_period = 0
                
                data = {
                    "measurements": {}
                }
                
                m = self.system.get_measurements()
                for leaf in m.keys():
                    ma = Leaf.average(m.get(leaf))
                    md = ma._as_dict()
                    
                    data["measurements"].update({
                        str(int(leaf.address)): md
                    })
                timestamp(data)
                data.update({
                    "errors": self.system.get_errors()
                })

                new_id = collection.insert_one(data)
                log.info(f"New log pushed: {new_id.inserted_id}")
                log.debug(f"Data: {data}")
                    
                # every once in a while, rescan the network
                if run_count % 100 == 0:
                    discover_result = self.system.discover()

                    data = {
                        "discovery": discover_result,
                        "system_info": {
                            "cpu_temp": get_cpu_temp_celsius()
                        }  
                    }
                    timestamp(data)
                    new_id = collection.insert_one(data)
                    log.info(f"New log pushed: {new_id.inserted_id}")
                    log.debug(f"Data: {data}")

                run_count += 1


print("creating logger")
log_filename = "/tmp/xerxes.log"

log = logging.getLogger()
logging.basicConfig(
    format="%(levelname)s: %(message)s",  # '%(asctime)s: %(name)s: %(levelname)s - %(message)s', 
    # datefmt='%m/%d/%Y %I:%M:%S %p',
    # filename=log_filename, 
    level=logging._nameToLevel[config.logging_level]
)


@app.route("/")
def hello_world():
    return f'{data.get("XS")._leaves}', 200


log.info(f"Logger started, log file: {log_filename}")
log.warning("Starting network.")

XN = XerxesNetwork(
    port=config.use_device
)
XN.init(
    baudrate=115200,
    timeout=config.port_timeout
)
data["XN"] = XN
log.info(XN)
log.info("Creating root (master)")
XR = XerxesRoot(Addr(0), XN)
data["XR"] = XR
log.warning("Master created")
log.info(str(XR))

log.warning("Creating node system")
XS = XerxesSystem(
    mode=Duplex.HALF,
    root=XR,
    std_timeout_s=config.network_timeout,
)
data["XS"] = XS
log.info("System created.")
log.warning("Discovering leaves on network...")
log.info(XS.discover())
log.warning([i.address for i in XS._leaves])

log.info("Connecting to database...")
shard = MongoClient(config.mongo_URI)
database = shard.get_database(config.use_database)
log.info("Creating collection...")
collection = database[HOSTNAME]
log.info(f"Database {database.name} connected")

log.info(f"Using collection: {database.name}.{HOSTNAME}")
log.info(f"Current working dir: {os.getcwd()}")

node = Runner(
    collection=collection,
    system=XS,
    sample_period=config.sample_period, 
    log_period=config.update_period
)
node.start()
data["node"] = node
log.info(f"Node: {node} worker started")
log.debug(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
