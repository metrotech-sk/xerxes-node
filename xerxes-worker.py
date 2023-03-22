#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import logging
import re
import dotenv
from serial import Serial
from typing import Dict, List
from xerxes_protocol import (
    XerxesNetwork, 
    XerxesRoot,
    Leaf
)
from xerxes_node.system import XerxesSystem, add_timestamp
from xerxes_node.uploader import Uploader
from yaml import load, dump
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from pprint import pprint as print

    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

MEASUREMENTS_DIR = "measurements"    

def load_config() -> Dict:
    """Load config from config.yaml and environment variables."""
    
    dotenv.load_dotenv()

    regex = r"(\$\{[\w]+\})"
    s_yaml = open("config.yaml").read()

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
    
    log.debug(f"Config loaded: {config}")
              
    return config
    
    
if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s: %(message)s",  # '%(asctime)s: %(name)s: %(levelname)s - %(message)s', 
        # datefmt='%m/%d/%Y %I:%M:%S %p',
        # filename=config.log.file, 
        level=logging.DEBUG
    )
    log.info("Loading config...")
    config = load_config()
    log.setLevel(config["log"]["level"])
    
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
    
    try:
        log.info("Uploader starting...")
        uploader.start()  # start uploader thread
        log.info("Uploader started. Starting system...")
        system.spin()  # start n-threads for each root
        log.info("System started.")
        log.debug(f"Living threads: {system.status()}")
        
        for i in (1,2):
            # sleep for upload period
            time.sleep(config["system"]["upload_period"])
            log.info("Dumping data...")
            system.dump(directory=MEASUREMENTS_DIR)
    finally:
        system.stop()
        uploader.stop()
    
    log.info("System stopped.")

