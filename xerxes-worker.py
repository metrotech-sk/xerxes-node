#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import logging
import dotenv
import signal
import sys
from serial import Serial
from typing import Dict
import struct
from pprint import pprint
from xerxes_protocol import (
    XerxesNetworkSingleton,
    XerxesRoot,
    Leaf,
    memory,
)
from pymongo import MongoClient, errors
from xerxes_node.system2 import Worker
from xerxes_node.uploader import Uploader
from yaml import load
from threading import Lock

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


log = logging.getLogger(__name__)


def load_config() -> Dict:
    """Load config from config.yaml and environment variables."""

    dotenv.load_dotenv()

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.yaml"
    )

    s_yaml = open(config_path).read()
    config: Dict = load(s_yaml, Loader=Loader)

    return config


class Accelerometer(Leaf):
    @property
    def fft(self):

        # read message buffer from sensor
        payload = self.read_reg_net(memory.MESSAGE_OFFSET, 128)
        payload += self.read_reg_net(memory.MESSAGE_OFFSET + 128, 128)
        # unpack 64 floats into list:
        vals = struct.unpack("64f", payload)
        data = {}
        data["spectrum"] = []
        for i in range(0, 60, 2):
            f = {
                "f": vals[i],
                "a": vals[i + 1],
            }
            data["spectrum"].append(f)
        data["main"] = {
            "f": vals[60],
            "a": vals[61],
        }
        return data
    
    @property
    def reset(self):
        self.reset_soft()
        return None


if __name__ == "__main__":
    config = load_config()
    # config log to show filename and line number
    logging.basicConfig(
        format="%(levelname)s [%(filename)s:%(lineno)s]: %(message)s",  # '%(asctime)s: %(name)s: %(levelname)s - %(message)s',
        # datefmt='%m/%d/%Y %I:%M:%S %p',
        # filename=config.log.file,
        level=logging.getLevelName(config["log"]["level"]),
    )

    log.debug(f"Config loaded: {config}")

    roots = {}
    for root in config["system"]["roots"]:
        _xn = XerxesNetworkSingleton(Serial(root["device"]))
        _xn.init(baudrate=root["baudrate"], timeout=root["timeout"])
        _xn.nlock = Lock()
        log.debug(f"Network created: {_xn}")

        _xr = XerxesRoot(my_addr=0xFE, network=_xn)
        log.debug(f"Root created: {_xr}")
        roots[root["label"]] = _xr

    log.debug(f"Roots created: {roots}")

    workers = {}

    for worker in config["system"]["workers"]:
        log.debug(f"Creating worker: {worker}")
        _xw = Worker(name=worker["label"])
        workers[worker["label"]] = _xw
        _leaves = []
        for leaf in worker["leaves"]:
            _xl = Accelerometer(addr=leaf["address"], root=roots[leaf["root"]])
            _xl.label = leaf["label"]
            _xl.values = leaf.get("values") if leaf.get("values") else []
            _xl.calls = leaf.get("calls") if leaf.get("calls") else []
            _leaves.append(_xl)
        _xw.setup(
            period=worker["period"],
            leaves=_leaves,
            workdir=config["system"]["work_dir"],
            name=worker["label"],
        )
        _xw.start()

    log.info("System created.")

    uri = os.getenv("XERXES_MONGO_URI")
    while True:
        try:
            database = MongoClient(uri).get_database(config["database"]["name"])
            break
        except errors.ConfigurationError:
                log.error("Not able to connect to the server. Trying again in 5s")
                time.sleep(5)
            
    uploader = Uploader(
        collection=database[config["database"]["collection"]],
        workdir=config["system"]["work_dir"],
        upload_period=config["uploader"]["upload_period"],
    )

    def sigint_handler(signal, frame):
        """Handle SIGINT and SIGTERM signal."""
        log.info(f"{signal} received. Stopping...")
        for worker in workers.values():
            worker.stop()
        uploader.stop()
        log.info("Exiting...")
        sys.exit(0)

    # register SIGTERM handler
    signal.signal(signal.SIGTERM, sigint_handler)
    signal.signal(signal.SIGINT, sigint_handler)

    try:
        log.info("Uploader starting...")
        uploader.start()  # start uploader thread
        log.info("Uploader started. Starting system...")
        pprint("Xerxes node started, workers: ")
        pprint(config["system"]["workers"])
        while True:
            time.sleep(1)
            # wait here for signal
    except KeyboardInterrupt:
        log.info("Keyboard interrupt. Stopping system...")
    finally:
        sigint_handler(signal.SIGINT, None)

    log.info("System stopped.")
