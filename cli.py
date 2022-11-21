#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
from typing import Callable, Dict, List, Union
from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from xerxes_protocol.network import NetworkError, XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
import os
import serial
import time
from rich import print

def get_int(text = ""):
    inp = None
    while inp is None:
        try:
            inp = int(input(text))
        except Exception as e:
            print(e)
            inp = None
    return inp
        

def select_pair(options: Dict):
    if(len(options.keys()) == 0):
        print("Nothing to select")
        return None
    
    if len(options.keys()) == 1:
        print(f"Using: {options[list(options.keys())[0]]}")
        return options[list(options.keys())[0]]
    
    for i in range(len(options.keys())):
        print(i, list(options.keys())[i])
        
    selection = False
    while not selection:
        try:
            key = int(input("Select option #: "))
            selection = options[list(options.keys())[key]]
        except IndexError:
            pass
        except ValueError:
            pass
    return selection
    
    
def select(l: List):
    if(len(l) == 0):
        print("Nothing to select")
        return None
    
    if len(l) == 1:
        print(f"Using: {l[0]}")
        return l[0]
    
    for i in range(len(l)):
        print(i, l[i])
    
    selection = None
    while selection is None:
        try:
            selection = l[int(input("Select option #: "))]
        except IndexError:
            pass
        except ValueError:
            pass
    return selection

devices = os.popen("ls /dev/|grep -e ttyUSB -e ttyACM").read().split("\n")
port = select(devices[:-1])

xn = XerxesNetwork(
    port=serial.Serial(
        port="/dev/"+port,  
        baudrate=115200,
        timeout=0.02)).init(
)
xr = XerxesRoot(
    my_addr=Addr(0xFE),
    network=xn
)

present = []
def discover():
    global present
    present = []
    
    start_addr = int(input("Start address: "))
    end_addr = int(input("End address: "))+1
    for i in range(start_addr, end_addr):
        ai = Addr(i)
        try:
            print(xr.ping(ai))
            present.append(ai)
            time.sleep(.01)
        except NetworkError:
            pass
        except TimeoutError:
            pass
    
    print("Adresses on bus: ", present)
        

def sync():
    print(xr.sync())
    

def fetch_all():
    global present
    for la in present:
        leaf = Leaf(la, root=xr)
        print(leaf.fetch())
        

def fetch_one():
    la = select(present)
    #if la:
    leaf = Leaf(
        addr=la, 
        root=xr
    )
    print(leaf.fetch())
        
        
def read_reg():
    la = select(present)
    leaf = Leaf(
        addr=la, 
        root=xr
    )
    regnr = get_int("Register number: ")
    val_type = select_pair({
        "uint8": "B",
        "uint32": "I",
        "int32": "i",
        "float": "f",
    })
    if val_type == "B":
        val = leaf.read_reg(reg_addr=regnr, length=1)
    else:
        val = leaf.read_reg(reg_addr=regnr, length=4)
    print(f"Reg: {regnr} = {struct.unpack(val_type, val.payload)[0]}")
    

def write_reg():
    la = select(present)
    leaf = Leaf(
        addr=la, 
        root=xr
    )
    regnr = get_int("Register number: ")
    val_type = select_pair({
        "uint8": "B",
        "uint32": "I",
        "int32": "i",
        "float": "f",
    })
    
    value = input("Input value: ")
    try:
        value = struct.pack(val_type, float(value))
    except:
        value = struct.pack(val_type, int(value))
    val = leaf.write_reg(reg_addr=regnr, value=value)
    print("Reply: ")
    print(val)

def reset_dev():
    la = select(present)
    leaf = Leaf(
        addr=la, 
        root=xr
    )
    leaf.reset_soft()
    time.sleep(.1)
    print(f"Leaf {leaf} restarted")
    

options = {
    "discover": discover,
    "sync": sync,
    "fetch": {
        "all": fetch_all,
        "one": fetch_one
    },
    "read register": read_reg,
    "write register": write_reg,
    "reset": reset_dev
}


def execute(options: Union[Dict, Callable]):
    selection = select(list(options.keys()))
    option = options[selection]
    if isinstance(option, dict):
        print(f"{selection}: ")
        execute(option)
    elif callable(option):
        option()
        
if __name__ == "__main__":
    while 1:
        try:
            execute(options)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)