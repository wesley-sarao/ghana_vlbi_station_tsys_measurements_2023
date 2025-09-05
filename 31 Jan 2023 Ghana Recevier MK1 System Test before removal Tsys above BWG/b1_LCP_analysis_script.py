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
import scipy
#%%
#Constants and variable definitions
#-----------------------------------------------------------------------------#
k=1.38e-23 #Boltzman's constand
ENR= 31.08 # ENR of Noise source
atten= -0 #Attenuation value of attenuator added on output of noise source.
            # NB: negative value for atten
            # Can alyso be used to compensate for cable losses
Tref_cold= 10.7 # Physical temperature of cold reference.
T0=290.0 # Reference temperature
Rbw=2e6 # Resolusion BW (Hz)

#%%
#Get data
date = "31-Jan-2023"
time = '10:00'
receiver = 'Ghana Receiver Mk1'
band = 'B1LCP'
meas = 'nom_gain_-5dB_BWG_mode_1'
hot_load_location = 'above beam waveguide'
assumed_tcold = '10.7 K'
temp_hot_load_degrees_C = 30.63 
sky_conditions = 'cloud cover 30-40%'
wind = 'No wind'
#-----------------------------------------------------------------------------
freq =np.load(band+'/DUTfreq.npy')
skyfreq = (2081 + 3500)*1e6 - freq # convert IF 2 to sky frequency
#Tref_hot=np.load('Tref_hot.npy') # DUT output measured noise tempeature for hot load (K)
Pout_hot=np.load(band+'/'+band+'_'+meas+'_hot.npy') # DUT output noise tempeature for cold load (K)
Pout_cold=np.load(band+'/'+band+'_'+meas+'_cold.npy') # Measured noise tempeature for calibrated hot load (K)

numPoints=len(freq)

#%%
#Calculations
#-----------------------------------------------------------------------------
#Calculate Tref_hot
#Tref_hot=T0*10**(ENR/10)-1
Tref_hot=273.15 + temp_hot_load_degrees_C # measured temperature in celcius + 273.15 
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
data_f = 264

#upconverted = 5749-(freq/1e6)


def plot_Gain():
    plt.figure(1)
    plt.clf()    
    
    # z = np.polyfit(freq[data_s:data_f]/1e6,
    #             dutG_dB[data_s:data_f],
    #             1)
    # p = np.poly1d(z)

    # plt.plot(skyfreq[data_s:data_f]/1e6, 
    #           p(freq[data_s:data_f]/1e6),
    #           color='orange',
    #           alpha = 0.8,
    #           label='slope = %2.2f dB' %(400*(p.c[0])))
    
    plt.plot(skyfreq/1e6,
          (dutG_dB),
          linewidth=1,
          color='r')
          # label ='ripple = %2.2f dB'%(np.max(p(freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))+np.max((dutG_dB[data_s:data_f])-p(freq[data_s:data_f]/1e6))))

    # print(np.mean(dutG_dB[data_s:data_f]))
    # print(np.std(dutG_dB[data_s:data_f]))

#    plt.plot(dutFreqVNA/1e6,dutGainVNA, linewidth=1,color='r', label='VNA')
    plt.legend(loc='best')
    plt.title(band+" gain slope and gain ripple")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Gain(dB)")
    plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
#    plt.ylim((50,65))
#    plt.ylim((00,15))
#    plt.ylim((00,15))
#    plt.xlim((700,832))
#    plt.xlim((5749-768-64,5749-768+64))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/Gains_'+band+'_'+meas+'.png', dpi=200)
    return



def plot_ripple():
    plt.figure(7)
    plt.clf()    
    
    
    z = np.polyfit(freq[data_s:data_f]/1e6,
               dutG_dB[data_s:data_f],
               1)
    p = np.poly1d(z)

    plt.plot(skyfreq[data_s:data_f]/1e6,
             p(freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]),
             color='orange',
             alpha = 0.8,
             label=' peak to peak gain ripple = %2.2f dB' %(np.max(p(freq[data_s:data_f]/1e6)-(dutG_dB[data_s:data_f]))+np.max((dutG_dB[data_s:data_f])-p(freq[data_s:data_f]/1e6))))
    
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
    # plt.ylim((-2,2))
#    plt.ylim((00,15))
#    plt.xlim((700,832))
    # plt.xlim((5749-768-64,5749-768+64))
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
    plt.plot(skyfreq/1e6,dutT, linewidth=1,color='b', label='Measured Noise Temperature')
    # plt.plot([4981-32,4981+32],[125,125], linewidth=1,color='r', label='Specification = 125 K')
    plt.fill([4981-32,4981-32,4981+32,4981+32],[125,140,140,125],
              color='red',
              alpha=0.3,
              hatch="/",
              edgecolor='black',
              label="Specification $<125K$")
    # plt.fill([4917,4917,5045,5045],[0,110,110,0],color='g',alpha=0.05,label="Specification <110K")
    # plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
    plt.fill([4981-64,4981-64,4981+64,4981+64],[0,140,140,0],
              color='g',
              alpha=0.07,
              label="4917 MHz to 5045 MHz")


    plt.title(date+' '+receiver+' '+ band+" $T_e$ \n Hot load "+hot_load_location+"\n Assumed $T_{cold}$ ="+assumed_tcold )

    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Noise Temperature (K)")
    plt.grid(b='on',
         which='both',
         color='black',
         linestyle='-',
         linewidth=0.5,
         alpha=0.5)
    plt.legend(loc="best")
    plt.ylim((80,140))
    plt.xlim((4850,5100))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'//Teff_'+band+'_'+meas+'.png', dpi=200)
    np.save(band+'//Teff_'+band+'_'+meas,dutT)
    return


def plot_Power():
    plt.figure(3)
    plt.clf()    
    plt.plot(skyfreq/1e6,Po_hot_dB, linewidth=1,color='r', label='Pout (hot load)')
    plt.plot(skyfreq/1e6,Po_cold_dB, linewidth=1,color='b', label='Pout (cold load)')
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
    plt.xlim((4781,5181))
    fig = plt.gcf()
    fig.set_size_inches(8, 6, forward=True)
    fig.savefig(band+'/NF_'+band+'_'+meas+'.png', dpi=200)
    return

#%%   
plot_Gain()
# plot_ripple()
plot_DUTTeff()
plot_Power()
# plot_NF()

#%% 
# # Noise temperature matching

# Teff_B1_LCP = np.load("B1LCP//Teff_B1LCP_nom_gain.npy")
# Teff_B1_RCP = np.load("B1RCP//Teff_B1RCP_nom_gain.npy")

# Teff_B1_LCP_mn = np.mean(Teff_B1_LCP[data_s:data_f]) 
# Teff_B1_RCP_mn = np.mean(Teff_B1_RCP[data_s:data_f]) 



# plt.figure(5)
# plt.clf()
# plt.plot(5749-freq/1e6,Teff_B1_LCP, linewidth=1, label='$T_e$ B1_LCP')
# plt.plot(5749-freq/1e6,Teff_B1_RCP, linewidth=1, label='$T_e$ B1_RCP')

# plt.plot([5749-freq[data_s]/1e6,5749-freq[data_f]/1e6],[Teff_B1_LCP_mn,Teff_B1_LCP_mn], linewidth=1, label='$T_e$ B1_LCP mean = %0.2f k'%Teff_B1_LCP_mn)
# plt.plot([5749-freq[data_s]/1e6,5749-freq[data_f]/1e6],[Teff_B1_RCP_mn,Teff_B1_RCP_mn], linewidth=1, label='$T_e$ B1_RCP mean = %0.2f k'%Teff_B1_RCP_mn)
# #plt.plot(5749-freq/1e6,Teff_B1_RCP_mn, linewidth=1, label='$T_e$ B1_RCP')
# #plt.plot([4917,5045],[-5,-5], linewidth=1,color='r', label='Spec')
# #plt.plot([4917,5045],[+5,+5], linewidth=1,color='r', label='Spec')
# #    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
# plt.title("band 1 noise temperature matching = %0.2f k" %(Teff_B1_LCP_mn-Teff_B1_RCP_mn))
# plt.xlabel("Frequency (MHz)")
# plt.ylabel("Noise Temperature (K)")
# plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
# plt.ylim((60,110))
# plt.xlim((4917,5045))
# plt.legend(loc='best')
# fig = plt.gcf()
# fig.set_size_inches(8, 6, forward=True)
# fig.savefig('band 1 noise temperature matching.png', dpi=200)
# #np.save(band+'/Teff_'+band+'_'+meas,dutT)



# #%% 
# # Noise temperature matching

# Teff_B1_LCP = np.load("B1LCP//Teff_B1LCP_nom_gain.npy")
# Teff_B1_RCP = np.load("B1RCP//Teff_B1RCP_nom_gain.npy")

# Teff_B1_LCP_mn = np.mean(Teff_B1_LCP[data_s:data_f]) 
# Teff_B1_RCP_mn = np.mean(Teff_B1_RCP[data_s:data_f]) 



# plt.figure(5)
# plt.clf()
# plt.plot(5749-freq/1e6,Teff_B1_LCP, linewidth=1, label='$T_e$ B1_LCP')
# plt.plot(5749-freq/1e6,Teff_B1_RCP, linewidth=1, label='$T_e$ B1_RCP')

# plt.plot([5749-freq[data_s]/1e6,5749-freq[data_f]/1e6],[Teff_B1_LCP_mn,Teff_B1_LCP_mn], linewidth=1, label='$T_e$ B1_LCP mean = %0.2f k'%Teff_B1_LCP_mn)
# plt.plot([5749-freq[data_s]/1e6,5749-freq[data_f]/1e6],[Teff_B1_RCP_mn,Teff_B1_RCP_mn], linewidth=1, label='$T_e$ B1_RCP mean = %0.2f k'%Teff_B1_RCP_mn)
# #plt.plot(5749-freq/1e6,Teff_B1_RCP_mn, linewidth=1, label='$T_e$ B1_RCP')
# #plt.plot([4917,5045],[-5,-5], linewidth=1,color='r', label='Spec')
# #plt.plot([4917,5045],[+5,+5], linewidth=1,color='r', label='Spec')
# #    plt.plot([6550,6950],[110,110], linewidth=1,color='r', label='Spec')
# plt.title("band 1 noise temperature matching = %0.2f k" %(Teff_B1_LCP_mn-Teff_B1_RCP_mn))
# plt.xlabel("Frequency (MHz)")
# plt.ylabel("Noise Temperature (K)")
# plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
# plt.ylim((60,110))
# plt.xlim((4917,5045))
# plt.legend(loc='best')
# fig = plt.gcf()
# fig.set_size_inches(8, 6, forward=True)
# fig.savefig('band 1 noise temperature matching.png', dpi=200)
# #np.save(band+'/Teff_'+band+'_'+meas,dutT)

#%%

Teff_B1_LCP_FH = np.load("B1LCP//Teff_B1LCP_nom_gain_-5dB_FH.npy")
Teff_B1_LCP_BWG = np.load("B1LCP//Teff_B1LCP_nom_gain_-5dB_BWG_mode_1.npy")


plt.figure(6)
plt.clf()
plt.plot(skyfreq/1e6,Teff_B1_LCP_FH, linewidth=1, label='$T_e$ B1_LCP above FH')
plt.plot(skyfreq/1e6,Teff_B1_LCP_BWG, linewidth=1, label='$T_e$ B1_LCP above BWG')

plt.title("band 1 LCP difference between Tsys taken above BWG and FH")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Noise Temperature (K)")
plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
plt.ylim((100,140))
plt.xlim((4900,5050))
plt.legend(loc='best')
fig = plt.gcf()
fig.set_size_inches(8, 6, forward=True)
fig.savefig(band+'/Teff_'+band+'_'+meas+ 'Beamwaveguide vs Feedhorn', dpi=200)
#np.save(band+'/Teff_'+band+'_'+meas Beamwaveguide vs Feedhorn,dutT)

#%%

Teff_B1_LCP_FH = np.load("B1LCP//Teff_B1LCP_nom_gain_-5dB_FH.npy")
Teff_B1_LCP_BWG = np.load("B1LCP//Teff_B1LCP_nom_gain_-5dB_BWG_mode_1.npy")


plt.figure(7)
plt.clf()

plt.plot(skyfreq/1e6,Teff_B1_LCP_BWG-Teff_B1_LCP_FH, linewidth=1, label='$T_e$ B1_LCP above BWG')

plt.title("band 1 LCP Tsys taken above BWG minus tsys taken above FH")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Noise Temperature (K)")
plt.grid(b='on',which='both',color='black', linestyle='-', linewidth=0.5)
plt.ylim((-10,10))
plt.xlim((4900,5050))
plt.legend(loc='best')
fig = plt.gcf()
fig.set_size_inches(8, 6, forward=True)
fig.savefig('band 1 BWG tsys minus FH tsys.png', dpi=200)
#np.save(band+'/Teff_'+band+'_'+meas,dutT)