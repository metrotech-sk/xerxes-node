#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import Add
from tabnanny import check
import serial, time, os, struct
import serial.rs485
import wiringpi

my_addr = b"\x00"

def checksum(message: bytes) -> bytes:
    summary = sum(message)
    summary ^= 0xFF  # get complement of summary
    summary += 1  # get 2's complement
    summary %= 0x100  # get last 8 bits of summary
    return summary.to_bytes(1, "big")


def send_msg(com, destination, payload: bytes):    
    SOH = b"\x01"
    SOT = b"\x02"

    msg = SOH  # SOH
    msg += (len(payload) + 6).to_bytes(1, "big")  # LEN
    msg += my_addr
    msg += destination #  DST
    msg += SOT
    msg += payload  # MSGID
    msg += checksum(msg)
    
    wiringpi.digitalWrite(1, 1)
    com.write(msg)
    time.sleep(0.001)
    wiringpi.digitalWrite(1, 0)
    #time.sleep(0.001)
    #com.write(os.urandom(128))

def read_msg(com):
    # wait for start of message
    next_byte = com.read(1)
    while next_byte != b"\x01":
        next_byte = com.read(1)
        if len(next_byte)==0:
            raise TimeoutError("No message in queue")
        else: 
            print(f"Received: {next_byte}")

    checksum = 0x01
    # read message length
    msg_len = int(com.read(1).hex(), 16)
    checksum += msg_len

    #read source and destination address
    src = com.read(1)
    dst = com.read(1)

    sot = com.read(1)

    for i in [src, dst, sot]:
        checksum += int(i.hex(), 16) 

    # read message ID
    msg_id_raw = com.read(4)
    if(len(msg_id_raw)!=4):
        raise IOError("Invalid message received")
    for i in msg_id_raw:
        checksum += i

    msg_id = struct.unpack("!I", msg_id_raw)[0]

    # read and unpack all data into array, assiming it is uint32_t, big-endian
    msg_array = []
    for i in range(int((msg_len-10)/4)):
        next_word = com.read(4)
        for i in next_word:
            checksum += i
        msg_array.append(struct.unpack("!I", next_word)[0])
    
    #read checksum
    rcvd_chks = com.read(1)
    checksum += int(rcvd_chks.hex(), 16)
    checksum %= 0x100
    if checksum:
        raise IOError("Invalid checksum received")

    return {
        "source": src,
        "destination": dst,
        "length": msg_len,
        "message_id": msg_id,
        "payload": msg_array 
        }

class Addr:
    def __init__(self, /, range_low=0, range_high=256, start=0):
        self._addr = start
        self._low = range_low
        self._high = range_high

    def __next__(self):
        self._addr += 1
        return self.addr.to_bytes(1, "big")

    def __call__(self):
        return self.addr.to_bytes(1, 'big')

    @property
    def addr(self):
        if self._addr >= self._high:
            self._addr = self._low
        return self._addr

if __name__ == "__main__":
    wiringpi.wiringPiSetup() 
    wiringpi.pinMode(1, 1)
    
    msgid = 0
    reply = {}
    A = Addr(range_low=1, range_high=4, start=1)
    
    com = serial.Serial(baudrate=115200, port="/dev/ttyS0")
    try:
        # com = serial.rs485.RS485()
        #com.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=False, rts_level_for_rx=True)

        com.open()

        # while True: send_msg(com, A(), struct.pack("!I", msgid))

        while 1:
            #time.sleep(0.02)
            msgid += 1
            send_msg(com, A(), struct.pack("!I", msgid))
            try:
                rpl = read_msg(com)
                while rpl.get("destination") != my_addr:
                    print("reading ", rpl.get("destination"))
                    rpl = read_msg(com)
                
                pl = rpl.get('payload')
                src, p, ti, te1, te2 = rpl.get('source'), pl[0]/1000, pl[1]/1000-273.15, pl[2]/1000-273.15, pl[3]/1000-273.15, 
                print(f"Device: {src}, p[mbar]: {p}, t_i: {ti}, t_e1: {te1}, t_e2: {te2}")
                next(A)
                
            except TimeoutError:
                pass
            except IOError:
                pass
            except KeyboardInterrupt:
                if com.is_open:
                    com.close()
                break

    finally:
        if com.is_open:
            com.close()