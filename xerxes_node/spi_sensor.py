#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spidev
from wiringpi import wiringPiSetupGpio, pinMode, digitalWrite
from typing import Tuple
import time


# we will be using the following pins
# GPIO 22               pin 15
# GPIO 9    (SPI0 MISO) pin 21
# GPIO 11   (SPI0 SCLK) pin 23


class SPI_Sensor:
    def __init__(self, spi_bus, spi_ch, spi_cs):
        self._spi = spidev.SpiDev(spi_bus, spi_ch)
        self._spi_cs = spi_cs
        self._spi.no_cs = True  # turn off SPI CS - do that manually

        wiringPiSetupGpio()
        pinMode(spi_cs, 1)  # set pin as Digital output

    def _cs_activate(self):
        digitalWrite(self._spi_cs, 0)

    def _cs_deactivate(self):
        digitalWrite(self._spi_cs, 1)

    def set_spi_speed(self, *, hz):
        self._spi.max_speed_hz = hz

    def _read_spi(self, len) -> list:
        return self._spi.readbytes(len)

    def __del__(self):
        self._spi.close() 


class ABP(SPI_Sensor):
    VALmin = 1638.0 # counts = 10% 2^14
    VALmax = 14745.0 # counts = 90% 2^14

    def __init__(self, spi_bus, spi_ch, spi_cs, *, p_min=0, p_max=60):
        super().__init__(spi_bus, spi_ch, spi_cs)
        self.p_min = p_min
        self.p_max = p_max

        self.set_spi_speed(hz=500000)
    
    def get_pressure_temp(self) -> Tuple[float, float]:
        try:
            self._cs_activate()  # Select peripheral
            rxdata = self._read_spi(4)
        finally:
            self._cs_deactivate()  # release slave

        b0 = rxdata[0]
        b1 = rxdata[1]
        t0 = rxdata[2]
        t1 = rxdata[3]

        status = b0 & 0b11000000;
        pval = ((b0 & 0b00111111)<<8) + b1;
        t = ((t0<<8) + (t1 & 0b11111000))>>5;

        temp = (t*200.0/2047.0)-50.0
        pressure = (((pval-self.VALmin)*(self.p_max-self.p_min))/(self.VALmax-self.VALmin)) + self.p_min    

        if status == 0:
            return pressure, temp
        if status == 0b1:
            raise ValueError("Sensor is in command mode")
        elif status == 0b10:
            raise ValueError("Stale data, sensor did not complete measurement after last data reading")
        else:
            raise ValueError("Sensor is in diagnostic condition")
    
    def get_pressure(self) -> float:
        return self.get_pressure_temp()[0]

    def get_temp(self) -> float:
        return self.get_pressure_temp()[1]
    

    @staticmethod
    def wait_for_next():
        time.sleep(0.001)