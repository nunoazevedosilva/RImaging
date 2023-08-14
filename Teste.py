# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 11:19:22 2023

@author: INESC
"""

import sys
import os
import logging
import argparse
import datetime
import statistics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from wasatch.WasatchBus    import WasatchBus
from wasatch.WasatchDevice import WasatchDevice
from wasatch.SpectrometerSettings import SpectrometerSettings

import time
import h5py

def Raman_data_saver(filename,spot_number, signal, position,  exp_properties):
    
    with h5py.File( filename, 'a') as output_file:
        data = output_file.create_group("data")
        
        spot = 'spot_'+str(spot_number)
        data.create_group(spot)
        data[spot].create_dataset('position', data = position)
        data[spot].create_dataset('raw_data', data = signal)
        
        if spot_number == 0:
            
            properties = output_file.create_group('properties')
            properties.create_dataset('x_data', data = exp_properties['x_data']) #wavelength or wavenumber
            properties.create_dataset('step_size', data = exp_properties['step_size'])
            properties.create_dataset('speed', data = exp_properties['speed'])
            properties.create_dataset('n_points', data = exp_properties['n_points'])
        
            
        
    return None


fname = 'teste.h5'

signal = np.random.rand(1000,1)

position = np.array([0,0])

properties = { 'x_data' : np.linspace(0, 1000, 1000),
              'step_size' : 2,
              'speed' : 10,
              'n_points': [10,5]                
            }

a = Raman_data_saver(filename = fname,spot_number=0, signal = signal, position= position, exp_properties = properties)