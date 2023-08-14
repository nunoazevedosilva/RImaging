# -*- coding: utf-8 -*-
"""
Class and controllers for stage Fiber Laser
"""


from Stages import *
from acquisicao_espectro import *
import sys

import matplotlib.pyplot as plt
from numpy import *
import time

class Raman_Imaging_System:
    
    def __init__(self, spectrometer_parameters = {}, stage_parameters = {}):
        
        self.stage = Stage_System(parameters = stage_parameters)
        self.spectrometer = Control_spectrometer(sys.argv[1:], spectrometer_parameters['integration_time'],
                                                 spectrometer_parameters['n_averages'])
        
        
    def close_spectrometer(self):
        self.spectrometer.close_device()
        
    
    def map(self, filename, x_points, y_points, dist_x, dist_y, target_wn):
        """
        Creates a map of the sample with a dimension (dist_x, dist_y) with a
        number of points correspondent to (x_points, y_points). Creats a map at
        of the intensities at the target wavenumber/wavelength.

        Parameters
        ----------
        filename : str
            File path.
        x_points : INT
            Number of points in the x-axis to be scanned.
        y_points : INT
            Number of points in the y-axis to be scanned.
        dist_x : FLOAT
            Total distance in the x-axis to be scanned.
        dist_y : FLOAT
            Total distance in the y-axis to be scanned.
        target_wn : FLOAT
            Target wavenumber/wavelength to be plotted in the naive map.

        Returns
        -------
        spectrum_data : 2D-array
            2D array with x_points,y_points with the corresponding spectrum at 
            each point.

        """
        
        
        #define list of x and y points
        x = linspace(0, dist_x, x_points)
        y = linspace(0, dist_y, y_points)
        
        #Integration time in seconds
        int_time_seconds = self.spectrometer.integration_time / 1000  # Convert to seconds

        #Creates empty array of n_xpoints*n_ypoints
        spectrum_data = np.zeros([x_points,y_points])       
        
        #Point number
        n_point = 0
        
        #Gets x and y velocity
        vel_x = self.stage.stage.get_speed()[0]
        vel_y = self.stage.stage.get_speed()[1]        
        
        
        #Properties to be fed to saver function
        prop = {'x_data' : None,
                'step_size' : [dist_x / x_points, dist_y / y_points],
                'speed' : [vel_x, vel_y],
                'n_points' : [x_points, y_points]
            }
        
        
        #Cycle to map
        for i in range(x_points):
            for j in range(y_points):
                self.stage.move_to(x[i], y[j])
                print('Collecting point '+ str(n_point+1)+' of '+str(x_points * y_points))
                
                spectrum_xval, spectrum = self.spectrometer.acquire_spec()
                
                value = spectrum[spectrum_xval.index(min(spectrum_xval, key=lambda x:abs(x-target_wn)))] # Gets intensity value at target wavenumber
                
                spectrum_data[i,j] = value
                time.sleep(1.1*int_time_seconds)    # Delay to give time to acquire spectrum
                
                prop['x_data'] = spectrum_xval
                
                Raman_data_saver(filename,spot_number = n_point, signal = spectrum, position = [x[i], y[j]],  exp_properties = prop)
                
                n_point += 1                
                
            
        plt.imshow(spectrum_data)
        
        return spectrum_data
    
    
    

if __name__ == "__main__": 
    
    
    spec_parameters = {'integration_time': 200,
                               'n_averages': 1}
    
    stage_parameters = {}
    
    RIS = Raman_Imaging_System(spectrometer_parameters = spec_parameters, 
                                stage_parameters = stage_parameters )
    
    
    RIS.stage.check_state()
    
    yr, month, day, hr, minute = map(int, time.strftime("%Y %m %d %H %M").split())
    filename = str(yr)+str(month)+str(day)+'_'+str(hr)+str(minute)+'.h5'
    RIS.map(filename, 50, 50, 20, 25, 831)    
    
    RIS.close_spectrometer()
    RIS.stage.turn_off()
    
    
    a = Raman_data_loader(filename)
    print(a)
