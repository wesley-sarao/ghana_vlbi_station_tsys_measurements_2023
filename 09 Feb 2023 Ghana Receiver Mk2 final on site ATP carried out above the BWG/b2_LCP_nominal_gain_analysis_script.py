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
Tref_cold= 10.7 #27 # Physical temperature of cold reference.
T0=290.0 # Reference temperature
Rbw=2e6 # Resolusion BW (Hz)

#%%
#Get data

date = "09-Feb-2023"
time = '10:55'
receiver = 'Ghana Receiver Mk2'
band = 'B2LCP'
meas = 'nom_gain' #'_20k_nd'
hot_load_location = 'on beam waveguide'
assumed_tcold = '10.7 K'
temp_hot_load_degrees_C = 31.5 # Read from the EMS 
sky_conditions = 'cloud cover 0%'
wind = 'no wind'


#-----------------------------------------------------------------------------
freq =np.load(band+'/DUTfreq.npy')
#Tref_hot=np.load('Tref_hot.npy') # DUT output measured noise tempeature for hot load (K)
Pout_hot=np.load(band+'/'+band+'_'+meas+'_hot.npy') # DUT output noise tempeature for cold load (K)
Pout_cold=np.load(band+'/'+band+'_'+meas+'_cold.npy') # Measured noise tempeature for calibrated hot load (K)

numPoints=len(freq)
#f_start=freq[0]
#f_stop=freq[numPoints-1]
#data=mv.Network('5GHzLCP_oldWGA.s2p')
#freqVNA=(data.frequency.f)
#s21=data.s21.s_db[:,0]  #Get S21 data
#a=np.where(freqVNA==F1)
#indexFstart=a[0][0]
#a=np.where(freqVNA==F2)
#indexFstop=a[0][0]
#dutGainVNA=s21[indexFstart:indexFstop]
#dutFreqVNA=freqVNA[indexFstart:indexFstop]

#%%
#Calculations
#-----------------------------------------------------------------------------
#Calculate Tref_hot
#Tref_hot=T0*10**(ENR/10)-1
Tref_hot=273+temp_hot_load_degrees_C
attenG=10**(atten/10)
attenT=T0*(1-attenG)/attenG
#Conversions


# Average data
avePout_hot=np.zeros(numPoints,dtype=float)
avePout_cold=np.zeros(numPoints,dtype=float)
Y=np.zeros(numPoints,dtype=float)
measTeff=np.zeros(numPoints,dtype=float)
dutG=np.zeros(numPoints,dtype=float)
dutT=np.zeros(numPoints,dtype=float)

i=0
for i in range (0,numPoints):
   avePout_hot[i]=np.average(Pout_hot[:,i])   #Calculate average Pout_hot
   avePout_cold[i]=np.average(Pout_cold[:,i])   #Calculate average Tref_hot

aveTout_hot=((avePout_hot))/(k*Rbw) # Calculate measured output temperature
aveTout_cold=((avePout_cold))/(k*Rbw) # Calculate measured output temperature


#Method as described in (EA-MK-000-DREP-09_2)
i=0
for i in range (0,numPoints):
    Y[i]=avePout_hot[i]/avePout_cold[i] # Calculate Y over frequency
    measTeff[i]=(Tref_hot-Tref_cold*Y[i])/(Y[i]-1) # measured effective temperature
#    Te_sa=(Th-Y_sa*Tc)/(Y_sa-1)
    dutT[i]=measTeff[i]*attenG-attenT*attenG
    dutG[i]=(aveTout_hot[i]-aveTout_cold[i])/(Tref_hot*attenG-Tref_cold) #Gain calculation

NF=10*np.log10((dutT/290)+1) # Convert to noise figure (dB)
dutG_dB=10*np.log10(dutG)-atten# Convert linear gain to dB
    
#Convert to power
Po_hot_dB=10*np.log10(avePout_hot/1e-3) 
Po_cold_dB=10*np.log10(avePout_cold/1e-3)


#%%
###-----------------------------------------------------------------------------#
###Plots
###-----------------------------------------------------------------------------#
##
# varables used to trim data down
data_s = 200
data_f = 600

upconverted=5982+freq/1e6


def plot_slope():
    plt.figure(1)
    plt.clf()    
    
    
    z = np.polyfit(5982+freq[data_s:data_f]/1e6,
               dutG_dB[data_s:data_f],
               1)
    p = np.poly1d(z)

    plt.plot(5982+freq[data_s:data_f]/1e6, p(5982+freq[data_s:data_f]/1e6),color='orange', alpha = 0.8,label='slope = %2.2f dB' %(400*(p.c[0])))
    
    plt.plot(5982+freq/1e6,
          (dutG_dB),
          linewidth=1,
          color='r',label ='ripple = %2.2f dB'%(np.max(p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))+np.max((dutG_dB[data_s:data_f])-p(5982+freq[data_s:data_f]/1e6))))

    print(np.mean(dutG_dB[data_s:data_f]))
    print(np.std(dutG_dB[data_s:data_f]))

    # print(np.max(p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))) 
#    print(np.max((dutG_dB[data_s:data_f])-p(5982+freq[data_s:data_f]/1e6)))  
#    plt.plot(dutFreqVNA/1e6,dutGainVNA, linewidth=1,color='r', label='VNA')
    plt.legend(loc='best')
    plt.title(date+' '+receiver+' '+band+' '+meas+" slope and gain ripple. Mean gain = %2.2f dB"%(np.mean(dutG_dB[data_s:data_f])))
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Gain (dB)")
    plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
    plt.ylim((50,65))
#    plt.ylim((-2,2))
#    plt.ylim((00,15))
#    plt.xlim((700,832))
    plt.xlim((5982+768-200,5982+768+200))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/gain_slope_'+band+'_'+meas+'.png', dpi=200)
    return
#
    

def plot_ripple():
    plt.figure(7)
    plt.clf()    
    
    
    z = np.polyfit(5982+freq[data_s:data_f]/1e6,
               dutG_dB[data_s:data_f],
               1)
    p = np.poly1d(z)

    plt.plot(5982+freq[data_s:data_f]/1e6, p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]),color='orange', alpha = 0.8,label=' peak to peak gain ripple = %2.2f dB' %(np.max(p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))+np.max((dutG_dB[data_s:data_f])-p(5982+freq[data_s:data_f]/1e6))))
    
#    plt.plot(5982+freq/1e6,
#          (dutG_dB),
#          linewidth=1,
#          color='r',label ='ripple = %2.2f dB'%(np.max(p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))+np.max((dutG_dB[data_s:data_f])-p(5982+freq[data_s:data_f]/1e6))))

#    print(np.max(p(5982+freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))) 
#    print(np.max((dutG_dB[data_s:data_f])-p(5982+freq[data_s:data_f]/1e6)))  
#    plt.plot(dutFreqVNA/1e6,dutGainVNA, linewidth=1,color='r', label='VNA')
    plt.legend(loc='best')
    plt.title(band+" gain ripple normalised to gain slope")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Gain ripple (dB)")
    plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
#    plt.ylim((50,65))
    plt.ylim((-2,2))
#    plt.ylim((00,15))
#    plt.xlim((700,832))
    plt.xlim((5982+768-200,5982+768+200))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/gain_ripple_'+band+'_'+meas+'.png', dpi=200)
    return

def plot_DUTTeff():
    
    # Use the seborn style
    import matplotlib
    # plt.style.use('seaborn')
    # matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
    
    
    
    plt.figure(2)
    plt.clf()
    plt.plot(freq/1e6+5982,dutT, linewidth=1,color='b', label='Measured Noise Temperature')
    plt.fill([6550,6550,6950,6950],[110,140,140,110],
             color='red',
             alpha=0.3,
             hatch="/",
             edgecolor='black',
             label="Specification $<110K$")    
    
    
    plt.title(date+' '+receiver+' '+ band+" $T_e$ \n Hot load "+hot_load_location+"\n Assumed $T_{cold}$ ="+assumed_tcold )

    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Noise Temperature (K)")
    plt.grid(b='on',
         which='both',
         color='black',
         linestyle='-',
         linewidth=0.5,
         alpha=0.5)
    plt.ylim((0,140))
    plt.xlim((6450,7000))
    plt.legend(loc="best")
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/Teff_'+band+'_'+meas+'.png', dpi=300)
    np.save(band+'/Teff_'+band+'_'+meas,dutT)
    return

      

def plot_Power():
    plt.figure(3)
    plt.clf()    
    plt.plot(freq/1e6,Po_hot_dB, linewidth=1,color='r', label='Pout (hot load)')
    plt.plot(freq/1e6,Po_cold_dB, linewidth=1,color='b', label='Pout (cold load)')
    plt.legend(loc='upper right')
    plt.title(band+" measured power")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power(dBm)")
    plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
#    plt.ylim((-120,-20))
#    plt.xlim((700,820))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/Power_'+band+'_'+meas+'.png', dpi=200)
    return
#
def plot_NF():
    plt.figure(4)
    plt.clf()    
    plt.plot(freq/1e6,NF, linewidth=1,color='g')#, label='Cal (hot)')
#   plt.legend(loc='upper right')
    plt.title(band+" noise figure")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("NF(dB)")
    plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
#    plt.ylim((0,1))
#    plt.xlim((700,820))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/NF_'+band+'_'+meas+'.png', dpi=200)
    return

#%%   
plot_slope()
plot_ripple()
plot_DUTTeff()
plot_Power()
# plot_NF()

#%% 
# # Noise temperature matching

# Teff_B2_LCP = np.load("B2LCP//Teff_B2LCP_nom_gain.npy")
# Teff_B2_RCP = np.load("B2RCP//Teff_B2RCP_nom_gain.npy")

# Teff_B2_LCP_mn = np.mean(Teff_B2_LCP[data_s:data_f]) 
# Teff_B2_RCP_mn = np.mean(Teff_B2_RCP[data_s:data_f]) 



# plt.figure(5)
# plt.clf()
# plt.plot(5982+freq/1e6,Teff_B2_LCP, linewidth=1, label='$T_e$ B2_LCP')
# plt.plot(5982+freq/1e6,Teff_B2_RCP, linewidth=1, label='$T_e$ B2_RCP')

# plt.plot([5982+freq[data_s]/1e6,5982+freq[data_f]/1e6],[Teff_B2_LCP_mn,Teff_B2_LCP_mn], linewidth=1, label='$T_e$ B2_LCP mean = %0.2f k'%Teff_B2_LCP_mn)
# plt.plot([5982+freq[data_s]/1e6,5982+freq[data_f]/1e6],[Teff_B2_RCP_mn,Teff_B2_RCP_mn], linewidth=1, label='$T_e$ B2_RCP mean = %0.2f k'%Teff_B2_RCP_mn)
# #plt.plot(5749-freq/1e6,Teff_B1_RCP_mn, linewidth=1, label='$T_e$ B1_RCP')
# #plt.plot([4917,5045],[-5,-5], linewidth=1,color='r', label='Spec')
# #plt.plot([4917,5045],[+5,+5], linewidth=1,color='r', label='Spec')
# #    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
# plt.title("band 2 noise temperature matching = %0.2f k" %(Teff_B2_LCP_mn-Teff_B2_RCP_mn))
# plt.xlabel("Frequency (MHz)")
# plt.ylabel("Noise Temperature (K)")
# plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
# plt.ylim((60,110))
# plt.xlim((6550,6950))
# plt.legend(loc='best')
# fig = plt.gcf()
# fig.set_size_inches(8, 6, forward=True)
# fig.savefig('band 2 noise temperature matching.png', dpi=200)
# #np.save(band+'/Teff_'+band+'_'+meas,dutT)

