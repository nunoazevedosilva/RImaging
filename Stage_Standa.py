# -*- coding: utf-8 -*-
"""
Class and controllers for stage Fiber Laser
"""

import serial
import time
import numpy as np

from ctypes import *
import time
import os
import sys
import tempfile
import re
from Axis import *


class Controller:
    
    def __init__(self):
        # variable 'lib' points to a loaded library
        # note that ximc uses stdcall on win
        self.devices_id = []
        self.initiate()
        
        

    def initiate(self):
        print("Library loaded")

        sbuf = create_string_buffer(64)
        lib.ximc_version(sbuf)
        print("Library version: " + sbuf.raw.decode().rstrip("\0"))

        # Set bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
        # wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
        # relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
        # In Python make sure to pass byte-array object to this function (b"string literal").
        lib.set_bindy_key(os.path.join(ximc_dir, "win32", "keyfile.sqlite").encode("utf-8"))

        # This is device search and enumeration with probing. It gives more information about devices.
        probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
        print(probe_flags)
        enum_hints = b"addr=172.17.20.108"
        # enum_hints = b"addr=" # Use this hint string for broadcast enumerate
        devenum = lib.enumerate_devices(probe_flags, enum_hints)
        print("Device enum handle: " + repr(devenum))
        print("Device enum handle type: " + repr(type(devenum)))

        dev_count = lib.get_device_count(devenum)
        
        if dev_count == 0:
            print("No devices detected. Shutting down.")
            sys.exit()
        
        self.devices_id = [None]*dev_count
        
        print("Device count: " + repr(dev_count))

        controller_name = controller_name_t()
        for dev_ind in range(0, dev_count):
            enum_name = lib.get_device_name(devenum, dev_ind)
            result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))
            if result == Result.Ok:
                name = "Enumerated device #{} name (port name): ".format(dev_ind) + repr(enum_name) + ". Friendly name: " + repr(controller_name.ControllerName) + "."
                self.devices_id[int(repr(controller_name.ControllerName)[-2])-1] = name

        for x in self.devices_id:
            print(x)
        
        open_name = None
        dev_list = []   # All the names of the devices are put in the dev_list list
        if len(sys.argv) > 1:
            open_name = sys.argv[1]
        elif dev_count > 0:
            for dev_ind in range(0, dev_count):
                open_name = lib.get_device_name(devenum, dev_ind)
                dev_list.append(open_name) # All the names of the devices are put in the dev_list list
        
        elif sys.version_info >= (3,0):
            # use URI for virtual device when there is new urllib python3 API
            tempdir = tempfile.gettempdir() + "/testdevice.bin"
            if os.altsep:
                tempdir = tempdir.replace(os.sep, os.altsep)
            # urlparse build wrong path if scheme is not file
            uri = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme="file", \
                    netloc=None, path=tempdir, params=None, query=None, fragment=None))
            open_name = re.sub(r'^file', 'xi-emu', uri).encode()

        #Organize the names by Ax1, ax2, ax3 and ax4
        n_dev_list = [None]*len(dev_list)
        for i in range(len(dev_list)):
            for j in range(len(self.devices_id)):
                if str(dev_list[i]) in self.devices_id[j]:
                    n_dev_list[j] = dev_list[i]
        dev_list = n_dev_list
        del(n_dev_list)


        if not open_name:
            exit(1)

        if type(open_name) is str:
            open_name = open_name.encode()

        for i in range(len(dev_list)):
            print("\nOpen devices " + repr(dev_list[i]))
            if i < 3:
                self.devices_id[i] = AxisXYZ(dev_list[i])
            else:
                self.devices_id[i] = AxisTheta(dev_list[i])
            'self.devices_id[i] = lib.open_device(dev_list[i])'
            print("Device id: Axis" + repr(i+1))




class Stage_Standa:
    
    def __init__(self,parameters):
        
        self.stage = Controller()
        
        self.convert_x = 2.5/1000 #resolution of 2.5um (step size)
        self.convert_y = 2.5/1000 
     
        self.convert_round_x =  1 
        self.convert_round_y =  1
        
        #self.convert_x = 2.5/(1000*20) #1 step is 20 counts
        #self.convert_y = 2.5/(1000*20) #102/817000
     
        #self.convert_round_x = 4000
        #self.convert_round_y = 4000
        self.wait = 500
        
        self.set_speed(5, 5)
        self.set_accel(5, 5)

        #self.set_speed(parameters['speed (mm/s)'])
        #self.set_accel(parameters['acceleration (mm/s**2)'])
        
    def check_state(self):
        is_ready = True
        current_position = self.get_position()
        
        return is_ready, current_position
        
    def turn_on(self): #function just to turn the axis on
        print('Turned on')
        pass
    
    def turn_off(self): #function just to turn the axis off
        self.go_home()
        print("Done")

    def close(self): #function just to turn the axis off
        self.go_home()
        print("\nClosing")
        for i in range(2): #len(self.stage.devices_id)
            self.stage.devices_id[i].close()
        print("Done")

    
    def go_home(self): #function just to send both axis to home
        self.stage.devices_id[0].move(lib,0,0)
        self.stage.devices_id[1].move(lib,0,0)
    

        self.stage.devices_id[0].wait_for_stop(lib,self.wait)
        self.stage.devices_id[1].wait_for_stop(lib,self.wait)
        
       
        return True, self.get_position()
    
    def move_to(self,x = None,y = None):
        if x != None:
            self.stage.devices_id[0].move(lib,int(round(x,3)//self.convert_x),int((round(x,3)%self.convert_x)*256/self.convert_x))
        if y != None:
            self.stage.devices_id[1].move(lib,int(round(y,3)//self.convert_y),int((round(y,3)%self.convert_y)*256/self.convert_y))
       
        
        self.stage.devices_id[0].wait_for_stop(lib,self.wait)
        self.stage.devices_id[1].wait_for_stop(lib,self.wait)
       

   
    ########################
    
    def get_position(self):
        x='{:.3f}'.format(float(self.stage.devices_id[0].get_position(lib)[0]) * self.convert_x + float(self.stage.devices_id[0].get_position(lib)[1])*self.convert_x/256)
        y='{:.3f}'.format(float(self.stage.devices_id[1].get_position(lib)[0]) * self.convert_y + float(self.stage.devices_id[1].get_position(lib)[1])*self.convert_y/256)
       
        return [x,y]
    
    def get_speed(self):        
        x='{:.3f}'.format(float(self.stage.devices_id[0].get_speed(lib))* self.convert_x*self.convert_round_x)
        y='{:.3f}'.format(float(self.stage.devices_id[1].get_speed(lib))* self.convert_y*self.convert_round_y)
       
        return [x,y]
    
    def get_accel(self):        
        x='{:.3f}'.format(float(self.stage.devices_id[0].get_accel(lib))* self.convert_x*self.convert_round_x)
        y='{:.3f}'.format(float(self.stage.devices_id[1].get_accel(lib))* self.convert_y*self.convert_round_y)
       
        return [x,y]

    def set_speed(self, x = None, y = None):
        if x != None:
            self.stage.devices_id[0].set_speed(lib,x/(self.convert_x*self.convert_round_x),int((round(x,3)%self.convert_x)*256/self.convert_x))
        if y != None:
            self.stage.devices_id[1].set_speed(lib,y/(self.convert_y*self.convert_round_y),int((round(y,3)%self.convert_y)*256/self.convert_y))
       
            
    def set_accel(self, x = None, y = None):
        if x != None:
            self.stage.devices_id[0].set_accel(lib,x/(self.convert_x*self.convert_round_x))#,int((round(x,3)%self.convert_x)*256/self.convert_x))
        if y != None:
            self.stage.devices_id[1].set_accel(lib,y/(self.convert_y*self.convert_round_y))#,int((round(y,3)%self.convert_y)*256/self.convert_y))
       

    def set_syncout_mode(self):
        
        self.stage.devices_id[0].set_syncout_mode(lib,0)
        
    def get_syncout_mode(self):
        
        self.stage.devices_id[0].get_syncout_mode(lib)
        self.stage.devices_id[1].get_syncout_mode(lib)
            
            

#
#device_id = new_experiment.stage_system.stage.stage.devices_id[0]
#sets = sync_out_settings_t()
#result = lib.get_sync_out_settings(device_id, byref(sets))
