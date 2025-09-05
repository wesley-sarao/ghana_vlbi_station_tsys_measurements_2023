#!/usr/bin/env python/
# -*- coding: utf-8 -*-
"""
Created: 15 September 2020y
@author: S. Malan
This script measures noise source temperature (Tref_hot), DUT power out for hot load (Pout_hot)
DUT power for cold load (Pout_cold).The DUT_Teff_analysis script is used to calculate Y factor, Teff and gain for DUT.
This script's primary function is to capture the data required to do the calculation.
"""


#%%
#Import functions that do the work
#----------#
import numpy as np
import pyvisa

#import time
#import telnetlib
#import matplotlib.pyplot as plt
#from SpectrumAnalyzerSocket import sa_sock #Import the Spectrum Analyser Socket Function
#import mwavepy as mv
#import pandas as pd
#import datetime
#from scipy import signal

# ------------------------
# import socket
import time
from numpy import double
#%%
#Constants and variable definitions
#-----------------------------------------------------------------------------#
f_start=(768-400) #Start frequency in MHz
f_stop=(768+400) #Stop frequency in MHz
#f_start=6550e6 #Start frequency
#f_stop=6950e6 #Stop frequency
numPoints=801 #Number of measurement points

# stop_f_set=f_stop
# start_f_set=f_start
# nr_points_set=numPoints

Rbw=2 #Resolution BW of spectrum analyser in MHz
Vbw=30 #Video BW of spectrum analyser in KHz
RefLev=-20 # Set reference level of spectrum analyser
Atten=10 #Set spectrum analyser attenuation
k=1.38e-23 #Boltzman's constand
numSweeps = 20 # Number of sweeps for each measurement

band = 'B2LCP'
meas = 'nom_gain_-5d_BWG_mode_3'  #_5k_nd'


#teff = np.load(band+'/Teff_'+band+'_'+meas+'.npy')
#teff_5k = np.load(band+'/Teff_'+band+'_'+meas+'_5k_nd.npy')
#teff_20k = np.load(band+'/Teff_'+band+'_'+meas+'_20k_nd.npy')


#%%

import pyvisa

rm = pyvisa.ResourceManager()

signal_shark = rm.open_resource('TCPIP0::10.8.88.40::5300::SOCKET')
# connect to signal shark on 10.8.88.40 on port 5300 using socket
signal_shark.read_termination = '\r\n'
signal_shark.write_termination = '\r\n'
signal_shark.timeout = 50000

print(signal_shark.query("*IDN?"))

#%%
# Set up the spectrum analyser


signal_shark.write('SYSTEM:REMOTE:DISPLAY OFF')
#disable GUI for higher performance

signal_shark.write('*RST')
#Reset signal shark

print(signal_shark.write("TASK:NEW? 'SPECTRUM'"))
#Start new task set instrument to spectrum - do not use RT_SPECTRUM only has 40 MHz span


signal_shark.write('SENSE:STOP')
#Stop the measuring system for configuration

# Check for errors
print(signal_shark.query('SYSTEM:ERROR:ALL?'))

print(signal_shark.write('SYSTem:REMote:TIMeout 20'))
print('Signal shark remote timeout: '+signal_shark.query('SYSTem:REMote:TIMeout?')+' s' )

#Configure the measurement task

# signal_shark.write('TASK:NEW')

print(signal_shark.write('SPECtrum:FREQuency:ENTRy:MODE FSTART_FSTOP'))
print(signal_shark.write('SENSE:ATTENUATOR: %idB' %Atten))
print(signal_shark.write('SPEC:FREQ:START %i MHZ' %f_start))
print(signal_shark.write('SPEC:FREQ:STOP %i MHZ' %f_stop))
#set the stop frequency
# print(signal_shark.write('SPEC:FREQ:STEP 1 MHZ'))
#set the frequency step
# time.sleep(1)
print(signal_shark.write('SPECTRUM:RBW %i MHz'%Rbw))
print('RBW:'+signal_shark.query('SPECTRUM:RBW?')+' Hz')


#Instead of VBW, we set the measurement time in milli seconds
meas_time = 100
print(signal_shark.write('SPECTRUM:MEAS:TIME %ims'%meas_time))
print('Meas_time:'+signal_shark.query('SPECTRUM:MEAS:TIME?')+' s per bin')


# print(signal_shark.write('SPECTRUM:VBW %i MHz'%Vbw))
#set the frequency step

start_f_set = double(signal_shark.query('SPECTRUM:FREQUENCY:START?'))
stop_f_set = double(signal_shark.query('SPECTRUM:FREQUENCY:STOP?'))
# step_f_set = signal_shark.query('SPECTRUM:DATA:FREQUENCY:STEP?')
#        stop_f = start_f + (nr_points-1)*delta_f
print(signal_shark.write('SPECTRUM:TRACE:ENABLE RMS,ON'))
print(signal_shark.write('SPECTRUM:TRACE:ENABLE PPk,OFF'))
print(signal_shark.write('SPECTRUM:SCAN:COUNT 1'))

print('Trace type:'+signal_shark.query('SPECTRUM:TRACE:LIST?'))

print('SA Start Freq: %s MHz, Stop Freq: %s MHz'% \
     (start_f_set*1e-6,stop_f_set*1e-6))

#%% Carry out measurement

# Run the measurement and return 0 on completion  
print(signal_shark.query('RUN:SINGLE?') ) 

# Update the measurment data
print(signal_shark.query('SPECTRUM:DATA:UPDATE?') ) 

#Stop the measurement
# print(signal_shark.write('SENSE:HOLD'))

# Fetch the measurement data
data=signal_shark.query('SPEC:DATA:LEVel? RMS')

nr_points_set = int(signal_shark.query('SPECTRUM:DATA:COUNT?'))
print('number of frequency points = %i'%nr_points_set)

#%% Generate frequency array


freq_delta_set = (stop_f_set-start_f_set)/(nr_points_set-1)    
# Get frequency data from Start_freq, Stop_Freq and Amount of Points

freq = np.arange(nr_points_set)*freq_delta_set + start_f_set 
# Generate a numpy array for frequency data (Hz)

np.save(band+'/DUTfreq',freq) # save a numpy array that contains frequency data

dataTrace=np.zeros((numSweeps,numPoints),dtype=float) # array for storing data



#%%
#Get data
#-----------------------------------------------------------------------------
# Measure Tref_hot
# keyIn = input('Connect hot load. Ready? (y/n):')
# if keyIn=='y':
#     i=0
#     for i in range (0,numSweeps):
        
#         # Run the measurement and return 0 on completion  
#         print(signal_shark.query('RUN:SINGLE?') ) 

#         # Update the measurment data
#         print(signal_shark.query('SPECTRUM:DATA:UPDATE?') ) 

#         #Stop the measurement
        
#         # print(signal_shark.write('SENSE:HOLD'))

#         # Fetch the measurement data
#         temp=(signal_shark.query('SPEC:DATA:LEVel? RMS'))  
#         temp2=temp.split(',')
#         dataTrace[i,:]=np.array(temp2,dtype=float) # Get trace data and change data into a numpy array (dBm)
#         print ("Tref_hot measurement # %i of %i" %(i+1,numSweeps))
#     Pout_hot=(10**(dataTrace/10)*1e-3) # Convert to linear power (W)
#     np.save(band+'/'+band+'_'+meas+'_hot',Pout_hot)

#%%

# # Measure Pout_cold
keyIn = input('Switch hot load off. Ready? (y/n):')
if keyIn=='y':
    i=0
    for i in range (0,numSweeps):
        
        # Run the measurement and return 0 on completion  
        print(signal_shark.query('RUN:SINGLE?') ) 

        # Update the measurment data
        print(signal_shark.query('SPECTRUM:DATA:UPDATE?') ) 

        #Stop the measurement
        # print(signal_shark.write('SENSE:HOLD'))

        # Fetch the measurement data
        temp=(signal_shark.query('SPEC:DATA:LEVel? RMS'))  
        temp2=temp.split(',')
        dataTrace[i,:]=np.array(temp2,dtype=float) # Get trace data and change data into a numpy array (dBm)
        print ("Tref_cold measurement # %i of %i" %(i+1,numSweeps))
    Pout_cold=(10**(dataTrace/10)*1e-3) # Convert to linear power (W)
    np.save(band+'/'+band+'_'+meas+'_cold',Pout_cold)

