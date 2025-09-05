#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created: 15 September 2020
@author: S. Malan
This  script reads in data captured using the DUT_Teff script. The expected data is Tref_hot, Pout_hot,
Pout_cold, freq.
The script calculates Teff and Gain using the Y-factor method
Additionally the script reads in a s2p file containing the gain data captured from a VNA which is 
then compared with the calculated gain.
"""
#%%
#Import functions that do the work
#----------#
import numpy as np
#import time
#import telnetlib
import matplotlib.pyplot as plt
#from SpectrumAnalyzerSocket import sa_sock #Import the Spectrum Analyser Socket Function
#import mwavepy as mv
#import pandas as pd
#import datetime
#from scipy import signal
#%%
#Constants and variable definitions
#-----------------------------------------------------------------------------#
k=1.38e-23 #Boltzman's constand
ENR= 31.08 # ENR of Noise source
atten= -0 #Attenuation value of attenuator added on output of noise source.
            # NB: negative value for atten
            # Can alyso be used to compensate for cable losses
Tref_cold= 3 # Physical temperature of cold reference.
T0=290.0 # Reference temperature
Rbw=3e6 # Resolusion BW (Hz)

#%%
#Get data

band = 'B1RCP'
meas = 'nom_gain_night'
#-----------------------------------------------------------------------------
freq =np.load(band+'/DUTfreq.npy')
#Tref_hot=np.load('Tref_hot.npy') # DUT output measured noise tempeature for hot load (K)
Pout_hot=np.load(band+'/'+band+'_'+meas+'_hot.npy') # DUT output noise tempeature for cold load (K)
Pout_cold=np.load(band+'/'+band+'_'+meas+'_cold.npy') # Measured noise tempeature for calibrated hot load (K)

numPoints=len(freq)

#%%
###-----------------------------------------------------------------------------#
###Plots
###-----------------------------------------------------------------------------#
##

teff = np.load(band+'/Teff_'+band+'_'+meas+'.npy')
teff_5k = np.load(band+'/Teff_'+band+'_'+meas+'_5k_nd.npy')
teff_20k = np.load(band+'/Teff_'+band+'_'+meas+'_20k_nd.npy')

plt.figure(1)
plt.clf()
plt.plot(5749-freq/1e6,teff, linewidth=1,color='r', label='$T_{e}$')
plt.plot(5749-freq/1e6,teff_5k, linewidth=1,color='r', label='$5k$')
plt.plot(5749-freq/1e6,teff_20k, linewidth=1,color='r', label='$20k$')

plt.plot([4917,5045],[110,110], linewidth=1,color='r', label='Spec')
#    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
plt.title(band+" effective noise temperature")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Noise Temperature (K)")
plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
plt.ylim((0,120))
plt.xlim((4917,5045))
plt.legend(loc='best')
fig = plt.gcf()
fig.set_size_inches(8, 6, forward=True)
#fig.savefig(band+'/Teff_'+band+'_'+meas+'.png', dpi=200)
#np.save(band+'/Teff_'+band+'_'+meas,dutT)

#%%


plt.figure(2)
plt.clf()
plt.plot(5749-freq/1e6,teff_5k-teff, linewidth=1,color='black',alpha=0.6 , label='5k trace')
#plt.plot(5749-freq/1e6,teff_20k-teff, linewidth=1,color='r', label='$20k$')
plt.plot([5749-freq[336]/1e6,5749-freq[464]/1e6],
         [np.mean(teff_5k[336:464]-teff[336:464]),
          np.mean(teff_5k[336:464]-teff[336:464])], 
          linewidth=3,
          color='#8F94CC',
          label='5k mean value over the band = %.2f k'%(np.mean(teff_5k[372:464]-teff[372:464])))

plt.fill_between([4917,5045,5045,4917],
                 [5.45,5.45,4.55,4.55],
                 facecolor='r',
                 alpha=0.1,
                 edgecolor='r',
                 linewidth=1,
                 linestyle='dashed',
                 label="Specification limit $5.45 k \geq 4.55 k $")



#plt.plot([4917,5045],[5.45,5.45], linewidth=1,color='r', label='Specification limit = 5.45 k')
#plt.plot([4917,5045],[4.55,4.55], linewidth=1,color='r', label='Specification limit = 4.55 k')
#    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
plt.title(band+" effective noise injection temperature")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Noise Temperature (K)")
plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
plt.ylim((0,10))
plt.xlim((4917,5045))
plt.legend(loc='best')
fig = plt.gcf()
fig.set_size_inches(8, 6, forward=True)
fig.savefig(band+'/5k.png', dpi=200)
#np.save(band+'/Teff_'+band+'_'+meas,dutT)

#%%

plt.figure(3)
plt.clf()
plt.plot(5749-freq/1e6,teff_20k-teff, linewidth=1,color='black', alpha=0.6, label='20k trace')
#plt.plot(5749-freq/1e6,teff_20k-teff, linewidth=1,color='r', label='$20k$')
plt.plot([5749-freq[336]/1e6,5749-freq[464]/1e6],
         [np.mean(teff_20k[336:464]-teff[336:464]),
          np.mean(teff_20k[336:464]-teff[336:464])],
          linewidth=3,
          color='#8F94CC',
          label='20k mean value over the band = %.2f k'%(np.mean(teff_20k[336:464]-teff[336:464])))


plt.fill_between([4917,5045,5045,4917],
                 [22.5,22.5,17.5,17.5],
                 facecolor='r',
                 alpha=0.1,
                 edgecolor='r',
                 linewidth=1,
                 linestyle='dashed',
                 label="Specification limit $22.5 k \geq 17.5 k $")

#plt.plot([4917,5045],[22.5,22.5], linewidth=1,color='b', label='Specification limit = 22.5 k')
#plt.plot([4917,5045],[17.5,17.5], linewidth=1,color='b', label='Specification limit = 17.5 k')
#    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
plt.title(band+" effective noise injection temperature")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Noise Temperature (K)")
plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
plt.ylim((0,25))
plt.xlim((4917,5045))
plt.legend(loc='lower left')
fig = plt.gcf()
fig.set_size_inches(8, 6, forward=True)
fig.savefig(band+'/20k.png', dpi=200)
#np.save(band+'/Teff_'+band+'_'+meas,dutT)
