##!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union


class Id: ...


class Id:    
    def __init__(self, id: Union[int, bytes]) -> None:
        if isinstance(id, int):
            assert(id >= 0)
        elif isinstance(id, bytes):
            id = int(id.hex(), 16)
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")

        self._id : int = id


    def to_bytes(self): ...


    @property
    def bytes(self):
        return self.to_bytes()


    def __repr__(self):
        return f"Id({self.to_bytes()})"

    
    @property
    def int(self):
        return self._id


    def __str__(self):
        return f"Id({self.to_bytes().hex()})"


    def __eq__(self, __o: Id) -> bool:
        assert isinstance(__o, Id), f"Invalid object type received, expected {type(Id(0))}, got {type(__o)} instead."
        return self._id == __o._id
        

class MsgIdMixin(Id):
    def to_bytes(self):
        return self._id.to_bytes(2, "big")


    def __len__(self):
        return 2


class DevIdMixin(Id):
    def to_bytes(self):
        return self._id.to_bytes(1, "big")


    def __len__(self):
        return 1



class MsgId(MsgIdMixin):   
    # Ping packet
    PING                          = MsgIdMixin(0x0000)
    
    # Reply to ping packet
    PING_REPLY                    = MsgIdMixin(0x0001)
    
    # Acknowledge OK packet
    ACK_OK                        = MsgIdMixin(0x0002)
    
    # Acknowledge NOK packet
    ACK_NOK                       = MsgIdMixin(0x0003)
    
    
    # Request to send measurements
    FETCH_MEASUREMENT             = MsgIdMixin(0x0100)
    
    # Synchronisaton message
    SYNC                          = MsgIdMixin(0x0101)
    
    
    # Pressure value + 2 temperatures
    PRESSURE_mPa_111TEMP          = MsgIdMixin(0x0403)    
    # Pressure value + second temperature only
    PRESSURE_mPa_110TEMP          = MsgIdMixin(0x0402)        
    # Pressure value + first temperature only
    PRESSURE_mPa_101TEMP          = MsgIdMixin(0x0401)
    # Pressure value w/o temperature*/ 
    PRESSURE_mPa_100TEMP          = MsgIdMixin(0x0400)
    
    
    # Strain value + 2 temperatures
    STRAIN_24BIT_11TEMP           = MsgIdMixin(0x1103)    
    # Strain value + second temperature only
    STRAIN_24BIT_10TEMP           = MsgIdMixin(0x1102)        
    # Strain value + first temperature only
    STRAIN_24BIT_01TEMP           = MsgIdMixin(0x1101)
    # Strain value w/o temperature
    STRAIN_24BIT_00TEMP           = MsgIdMixin(0x1100)

    
    # 2 distance values, 0-22000um, no temp
    DISTANCE_22MM                 = MsgIdMixin(0x4000)
    # 2 distance values, 0-225000um, no temp
    DISTANCE_225MM                = MsgIdMixin(0x4100)
    

    # 2 angle values, X, Y (-90°, 90°
    ANGLE_DEG_XY                  = MsgIdMixin(0x3000)


    def __repr__(self):
        return f"MsgId(0x{self.to_bytes().hex()})"


    def __str__(self):
        return self.__repr__()


class DevId(DevIdMixin):
    # Pressure sensors */
    # pressure sensor range 0-600mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK */
    PRESSURE_600MBAR_2TEMP    = DevIdMixin(0x03)
    # pressure sensor range 0-60mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK */
    PRESSURE_60MBAR_2TEMP     = DevIdMixin(0x04)
    
    # Strain sensors */
    # strain-gauge sensor range 0-2^24, 2 external temperature sensors -50/150°C output: mK */
    STRAIN_24BIT_2TEMP        = DevIdMixin(0x11)
    
    # I/O Devices */
    # I/O device, 8DI/8DO (8xDigital Input, 8xDigital 0utput) */
    IO_8DI_8DO                = DevIdMixin(0x20)
    
    
    # Inclinometers and accelerometers */
    # Inclinometer SCL3300 */
    ANGLE_XY_90               = DevIdMixin(0x30)
    
    
    # Distance sensors */
    # Distance sensor 0-22mm, resistive, linear*/
    DIST_22MM                 = DevIdMixin(0x40)
    # Distance sensor 0-225mm, resistive, linear*/
    DIST_225MM                = DevIdMixin(0x41)


    def __repr__(self):
        return f"DevId(0x{self.to_bytes().hex()})"
    
    
    def __str__(self):
        return self.__repr__()