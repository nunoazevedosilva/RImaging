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

log = logging.getLogger(__name__)


def Raman_data_saver(filename,spot_number, signal, position,  exp_properties):
    """
    Saver function.
    
    Parameters
    ----------
    filename : STR
       
    spot_number : INT
        
    signal : ARRAY
        Numpy array with the raw data.
    position : TYPE
        [x,y] position.
    exp_properties : DICT
        Experimental properties with the following keys: x_data, step_size, speed, n_points.
            
    Returns
    -------
    None.

    """
    
    with h5py.File( filename, 'a') as output_file:
        
        if spot_number == 0:
            data = output_file.create_group("data")
            
        data = output_file['data']
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
        
    
def Raman_data_loader(filename):

    with h5py.File( filename, 'a') as output_file:
         
        properties = output_file['properties']
        
        exp_properties = {'step_size' : np.array(properties['step_size'])[0],
                          'speed' : np.array(properties['speed']),
                          'n_points' : np.array(properties['n_points'])
            }
        
        wavelengths = np.array(output_file['properties']['x_data'])
        
        
        spot_numbers = [int(s.split('_')[-1]) for s in list(output_file['data'].keys()) if 'spot' in s ]
        
        Nx,Ny = output_file['properties']['n_points'][0], output_file['properties']['n_points'][1]
        Nl = len(wavelengths)
        spectral_signal = np.zeros([Nx,Ny,Nl])
        
        
        for _i, spot_number in enumerate(spot_numbers):

            ix, iy = int(spot_number%Nx), int(spot_number//Nx)
            
            spot = 'spot_'+str(spot_number)
            data = np.array(output_file['data'][spot]['raw_data'])
                      
            spectral_signal[ix,iy,:] = data
            

    return spectral_signal, wavelengths, exp_properties


class Control_spectrometer():
    def __init__(self, argv, integration_time, avg):
        """

        Parameters
        ----------
        argv : TYPE
            Parser for command-line options, arguments and sub-commands.
        integration_time : INT
            Integration time (ms).
        avg : INT
            Number of averages.

        Returns
        -------
        None.

        """
        
       
        # Locate device
        bus = WasatchBus()
        if not bus.device_ids:
            print("no spectrometers found")
            sys.exit(1)
        
        # Prints ID of device
        device_id = bus.device_ids[0]
        print("found %s" % device_id)
        
        
        device = WasatchDevice(device_id)
        if not device.connect().data:
            print("connection failed")
            sys.exit(1)
        
        # Prints parameters of device
        print("connected to %s %s with %d pixels from (%.2f, %.2f)" % (
            device.settings.eeprom.model,
            device.settings.eeprom.serial_number,
            device.settings.pixels(),
            device.settings.wavelengths[0],
            device.settings.wavelengths[-1]))

        self.device = device        # WasatchDevice
        self.fid = device.hardware  # FeatureInterfaceDevice
        
        
        settings = SpectrometerSettings()
        self.wavelength=device.settings.wavelengths
        self.wavenumber=device.settings.wavenumbers
        
        #settings for acquisition
        #define integration time #max=5000ms #min=8ms
        self.integration_time = integration_time
        self.avg = avg

    
    
    
        
# =============================================================================
#     def parse_args(self, argv):
#         parser = argparse.ArgumentParser(description="Collect spectra")
#         parser.add_argument("--outfile", type=str, default="spectra.csv", help="where to write spectra")
#         parser.add_argument("--log-level", type=str, default="INFO", help="logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL]")
#         return parser.parse_args(argv)
# =============================================================================

# =============================================================================
#     def acquire_spectrum(self):
# 
#         # let TEC settle
#         '''while True:
#             now = datetime.datetime.now()
#             temp = self.fid.get_detector_temperature_degC().data
#             if "y" in input(f"{now} temperature {temp:+8.2f}C Start collection? (y/[n]) ").lower():
#                 break'''
#         now = datetime.datetime.now()
#         temp = self.fid.get_detector_temperature_degC().data
#         
#         with open(self.args.outfile, "w") as outfile:
#             outfile.write("time, temperature, integration time (ms), min, max, median, mean, stdev, rms, spectra\n")
#             
#             now = datetime.datetime.now()
# 
# 
#             temp = self.fid.get_detector_temperature_degC().data
#             
#             #define integration time
#         
#             self.fid.set_integration_time_ms(self.ms)
#             self.device.settings.scans_to_average=self.avg
# 
#             spectrum = np.asarray(self.fid.get_line().data.spectrum, dtype=np.float32)
#             values = ", ".join([ str(y) for y in spectrum ])
#             
#        
#         
#             plt.plot(self.wavenumber,spectrum)
#             lo = min(spectrum)
#             hi = max(spectrum)
#             median = np.median(spectrum)
#             mean = np.mean(spectrum)
# 
#             stdev = np.std(spectrum)
#             rms = np.sqrt(np.mean(spectrum**2))
#             print('acquired')
#             
# 
#             
#             #saving the spectrum automatically to a file
#             #odir=os.getcwd()
#             #newdir=odir+"\\spectra"
#             
#             #df = pd.DataFrame(list(zip(self.wavenumber, spectrum)),columns =['Wavenumber(cm-1)', 'Counts'])
#             #df.to_csv(newdir + "\\" + self.filename + '.csv', sep='\t')
# 
#             outfile.write(f"{now}, {temp:.2f}, {self.ms}, {lo}, {hi}, {median:.2f}, {mean:.2f}, {stdev:.5e}, {rms:.5e}, {values}\n")
# 
#         #self.device.disconnect()
#         return self.wavenumber,spectrum
# =============================================================================
    

    
    def acquire_spec(self):
        """
        Acquires spectrum.

        Returns
        -------
        TYPE
            DESCRIPTION.
        spectrum : TYPE
            DESCRIPTION.

        """
        now = datetime.datetime.now()   #Get time


        temp = self.fid.get_detector_temperature_degC().data     #Get temperature
                                                        
        #define integration time
        self.fid.set_integration_time_ms(self.integration_time)
        
        #Define number of averages
        self.device.settings.scans_to_average=self.avg

        #Get spectrum
        spectrum = np.asarray(self.fid.get_line().data.spectrum, dtype=np.float32)
        
        return self.wavenumber, spectrum
    
    def close_device(self):
        self.device.disconnect()



if __name__ == "__main__": 
    test = Control_spectrometer(sys.argv[1:],200,1)
    spectrum = test.acquire_spec()
    

# =============================================================================
# #Testing saver/loader functions
#     position=[1,1]
#     prop = {'x_data': test.wavenumber,
#             'step_size': 0,
#             'speed': 10,
#             'n_points': [10,10]
#         }
#     
#     filename = 'teste5.h5'
#     
#     Raman_data_saver(filename, 0, spectrum[1], position,  exp_properties = prop)
# 
#     loader = Raman_data_loader(filename=filename)
# =============================================================================


    
    test.close_device()