from ctypes import *
import time
import os
import sys
import tempfile
import re

if sys.version_info >= (3,0):
    import urllib.parse


#directories must be defined in order to get the libximc package and pyximc.py
cur_dir = os.path.abspath(os.path.dirname(__file__))
"""This script assumes that it is in a folder where and it's parent folder as libximc package in it
It is then necessary to get the parent directory"""

par_dir = os.path.abspath(cur_dir)
ximc_dir = os.path.join(par_dir, r"libximc-2.13.6-all\ximc-2.13.6\ximc") #This str is the directory relative to the parent dir to get ximc
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)  # add ximc.py wrapper to python path

if sys.platform in ("win32", "win64"):
    libdir = os.path.join(ximc_dir, "win64")
    
    os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll

try:
    
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the testpython.py and pyximc.py files. See developers' documentation for details.")
    sys.exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    sys.exit()




"""So far it works
In this script, for starts, we want to send information to the controller so as to move it, but
also we want to know where it is at a given moment."""

class AxisXYZ:
    def __init__(self,name):
        self.name = name
        self.device = self.open()
        
    def open(self):
        ax = lib.open_device(self.name)
        return ax

    def close(self):
        lib.close_device(byref(cast(self.device, POINTER(c_int))))

    def info(self,lib):  #Gives info about the device
        print("\nGet device info")
        x_device_information = device_information_t()
        result = lib.get_device_information(self.device, byref(x_device_information))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Device information:")
            print(" Manufacturer: " +
                    repr(string_at(x_device_information.Manufacturer).decode()))
            print(" ManufacturerId: " +
                    repr(string_at(x_device_information.ManufacturerId).decode()))
            print(" ProductDescription: " +
                    repr(string_at(x_device_information.ProductDescription).decode()))
            print(" Major: " + repr(x_device_information.Major))
            print(" Minor: " + repr(x_device_information.Minor))
            print(" Release: " + repr(x_device_information.Release))


    def status(self,lib):    #Gives info about device status
        print("\nGet status")
        x_status = status_t()
        result = lib.get_status(self.device, byref(x_status))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Status.Ipwr: " + repr(x_status.Ipwr))
            print("Status.Upwr: " + repr(x_status.Upwr))
            print("Status.Iusb: " + repr(x_status.Iusb))
            print("Status.Flags: " + repr(hex(x_status.Flags)))


    def get_position(self,lib):  #Returns the position in steps and microsteps
        #print("\nRead position")
        x_pos = get_position_t()
        result = lib.get_position(self.device, byref(x_pos))
        #print("Result: " + repr(result))
        #if result == Result.Ok:
        #    print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
        #print("-----------")
        #print(x_pos.Position)
        #print(x_pos.uPosition)
        #print("-----------")
        return x_pos.Position, x_pos.uPosition


    def move(self,lib, distance, udistance):
        #print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
        result = lib.command_move(self.device, distance, udistance)
        #print("Result: " + repr(result))


    def wait_for_stop(self,lib, interval):
        #print("\nWaiting for stop")
        result = lib.command_wait_for_stop(self.device, interval)
        #print("Result: " + repr(result))


    def get_speed(self,lib):
        #print("\nGet speed")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = lib.get_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        #print("Speed is " + str(mvst.Speed) + str(mvst.uSpeed))
        
        return mvst.Speed
    
    def get_accel(self,lib):
        #print("\nGet speed")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = lib.get_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        #print("Speed is " + str(mvst.Accel))
        
        return mvst.Accel

                
    def set_speed(self,lib, speed, uspeed = 0):
        #print("\nSet speed")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = lib.get_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        #print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed))
        # Change current speed
        mvst.Speed = int(speed)
        #mvst.uSpeed = int(uspeed)
        # Write new move settings to controller
        result = lib.set_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Write command result: " + repr(result))
        
        
    def set_accel(self,lib, accel):
        #print("\nSet acceleration")
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = lib.get_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        #print("The acceleration was equal to {0}. We will change it to {1}".format(mvst.Accel, accel))
        # Change current acceleration
        mvst.Accel = int(accel)
        # Write new move settings to controller
        result = lib.set_move_settings(self.device, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        #print("Write command result: " + repr(result))


    def set_microstep_mode_256(self,lib):
        print("\nSet microstep mode to 256")
        # Create engine settings structure
        eng = engine_settings_t()
        # Get current engine settings from controller
        result = lib.get_engine_settings(self.device, byref(eng))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        # Change MicrostepMode parameter to MICROSTEP_MODE_FRAC_256
        # (use MICROSTEP_MODE_FRAC_128, MICROSTEP_MODE_FRAC_64 ... for other microstep modes)
        eng.MicrostepMode = MicrostepMode.MICROSTEP_MODE_FRAC_256
        # Write new engine settings to controller
        result = lib.set_engine_settings(self.device, byref(eng))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))    


    def set_position(self,lib, position):
        print("\nSet position")
        # Create point settings structure
        ptst = get_position_t()
        #print(".................")
        #print(ptst.Position)
        #print(ptst.uPosition)
        #print(ptst.EncPosition)
        #print(".................")
        # Get current position settings from controller
        result = lib.get_position(self.device,byref(ptst))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        #print("The position was {0}. We will move it to {1}".format(ptst.Position, position))
        #Change current position
        ptst.Position = int(position)
        # Write new position settings to controller
        result = lib.command_set_position(self.device, position)
        # Print comand return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))

    def home(self):
        self.move(lib,0,0)
        self.wait_for_stop(lib,100)

    def get_syncout_mode(self, lib):
        
        print("\nGet sync out mode")
        # Create engine settings structure
        sets = sync_out_settings_t()
        # Get current engine settings from controller
        result = lib.get_sync_out_settings(self.device, byref(sets))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        
        print(sets.SyncOutFlags)
        print(sets.SyncOutPulseSteps)
        print(sets.SyncOutPeriod)
        print(sets.Accuracy)
        print(sets.uAccuracy)
    
    def set_syncout_mode(self, lib, mode):
        
        print("\nSet sync out mode")
        # Create engine settings structure
        sets = sync_out_settings_t()
        # Get current engine settings from controller
        result = lib.get_sync_out_settings(self.device, byref(sets))
        print("Write command result: " + repr(result))   
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        # Change SYNCOUT_MODE to enable
        # (use number of pulse steps)
        print('Syncout - '+ str(sets.SyncOutFlags))
        print('Syncout steps - '+ str(sets.SyncOutPulseSteps))
        
        
        
        
        sets.SyncOutFlags = SyncOutFlags.SYNCOUT_ENABLED + SyncOutFlags.SYNCOUT_INVERT + SyncOutFlags.SYNCOUT_ONPERIOD + SyncOutFlags.SYNCOUT_IN_STEPS
        
        #sets.SyncOutPulseSteps = int(30)
        
        result = lib.set_sync_out_settings(self.device, byref(sets))
        print("Write command result: " + repr(result))   
        
        result = lib.get_sync_out_settings(self.device, byref(sets))
        print("read command result: " + repr(result))
        
        print('Syncout - '+ str(sets.SyncOutFlags))
        
        print('Syncout steps - '+ str(sets.SyncOutPulseSteps)) ############steps pulse duration
        print('Syncout period - '+ str(sets.SyncOutPeriod)) ####### steps/counts
        print('Syncout accuracy - '+ str(sets.Accuracy))
        print('Syncout uaccuracy - '+ str(sets.uAccuracy))
        
        
#        
#      
#       sets.SyncOutPulseSteps = int(20)
        # Write new syncout settings to controller
#       result = lib.set_sync_out_settings(self.device, byref(sets))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))         

    
    
   


