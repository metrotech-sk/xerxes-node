#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import logging
import re
import dotenv
import signal
import sys
from serial import Serial
from typing import Dict
from xerxes_protocol import (
    XerxesNetwork, 
    XerxesRoot,
    Leaf
)
from xerxes_node.system import XerxesSystem
from xerxes_node.uploader import Uploader
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

    
log = logging.getLogger(__name__)

MEASUREMENTS_DIR = "/tmp/measurements"    

def load_config() -> Dict:
    """Load config from config.yaml and environment variables."""
    
    dotenv.load_dotenv()
    
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.yaml"
    )

    regex = r"(\$\{[\w]+\})"
    s_yaml = open(config_path).read()

    def replace_env(match: str) -> str:
        return os.environ[match.group(1).lstrip("${").rstrip("}")]

    config_str = re.sub(
        regex,
        replace_env,
        s_yaml
    )

    config: Dict = load(
        config_str, 
        Loader=Loader
    )
    
              
    return config


def sigint_handler(signal, frame):
    """Handle SIGINT and SIGTERM signal."""
    log.info(f"{signal} received. Stopping...")
    system.stop()
    uploader.stop()
    log.info("Exiting...")
    sys.exit(0)
    
    
if __name__ == "__main__":
    config = load_config()
    # config log to show filename and line number
    logging.basicConfig(
        format="%(levelname)s [%(filename)s:%(lineno)s]: %(message)s",  # '%(asctime)s: %(name)s: %(levelname)s - %(message)s', 
        # datefmt='%m/%d/%Y %I:%M:%S %p',
        # filename=config.log.file, 
        level=logging.getLevelName(config["log"]["level"])
    )

    log.debug(f"Config loaded: {config}")
    
    roots = []
    for network in config["system"]["networks"]:
        _xn = XerxesNetwork(
            Serial(network["device"])
            )
        _xn.init(
            baudrate=network["baudrate"],
            timeout=network["timeout"]
        )
        log.debug(
            f"Network created: {_xn}"
        )
        
        _xr = XerxesRoot(
            my_addr=0xFE,
            network=_xn
        )
        log.debug(
            f"Root created: {_xr}"
        )
        roots.append(_xr)
        
        leaves = []
        for leaf in network["leaves"]:
            _xl = Leaf(
                addr=leaf["address"],
                root=_xr
            )
            
            # pass these values with leaves
            _xl.label = leaf["label"]
            _xl.process_values = leaf["values"]
                
            log.debug(
                f"Leaf created: {_xl}"
            )
            leaves.append(_xl)
            
        # REWORK: this is a hack, should be done in XerxesRoot?
        # pass leaves with corresponding root
        _xr.leaves = leaves
                

    log.info("System created.")
    
    database = config["database"]
    uploader = Uploader(
        uri=database["uri"],
        database=database["name"],
        collection=database["collection"],
        directory=MEASUREMENTS_DIR
    )
    system = XerxesSystem(
        roots=roots,
        sample_period=config["system"]["sample_period"],
    )

    # register SIGTERM handler
    signal.signal(signal.SIGTERM, sigint_handler)
    signal.signal(signal.SIGINT, sigint_handler)
    
    try:
        log.info("Uploader starting...")
        uploader.start()  # start uploader thread
        log.info("Uploader started. Starting system...")
        system.spin()  # start n-threads for each root
        log.info("System started.")
        log.debug(f"Living threads: {system.status()}")
        
        while(True):
            # sleep for upload period
            time.sleep(config["system"]["upload_period"])
            log.info("Dumping data...")
            system.dump(directory=MEASUREMENTS_DIR)
            if not uploader.alive():
                uploader.start()
    except KeyboardInterrupt:
        log.info("Keyboard interrupt. Stopping system...")
    finally:
        system.stop()
        uploader.stop()
    
    log.info("System stopped.")

