#!/usr/bin/python
#
# spec_wavecal.py
#
# A class that provides a GUI for calibrating the wavelengths (dispersion,
#  offset) of an extracted spectrum
#
# Class WAVECAL:
#
#  __INIT__: The main program
#  ONCLICK: finds the nearest x-coordinate point clicked
#  ONPICK: Mouse right-click removes a point defined using ONCLICK
#  ONTYPE: Two options
#   <ENTER>: Perform the wavlength calibration
#   "R": Resets the clicked data points -- allows you to re-do wavecal
#
# Dependencies:
#  
#  pylab
#  numpy
#  scipy
#  sys
#  os
#
# History:
#  DGW, 13 May 2016: Created using specnorm.py as a template
#  DGW, 17 May 2016: Code is commented
#  AJC, 1 June 2016: Fixed bug in ONTYPE, 'r', so that spectrum is re-plotted
#                    automatically
#  DGW, 30 Jun 2016: If four or more wavelength values are sent, then a 
#                      quadratic fit is made to the datapoints. 
#                    This provides a substantially more accurate wavelength 
#                      calibration than a linear fit.

import pylab as plt
import numpy as np
from scipy.optimize import curve_fit
import sys
import os

class wavecal:

    # __INIT__
    # Inputs:
    #  SPEX: the array of extracted spectra returned from SPEC_EXTRACT
    #  WVS: a list of wavelength values from the lines that will be used
    #   for wavelength calibration
    #  WINDOW: The option exists to average points near the clicked point
    #   and use that average value as the selected x-coordinate. Currently
    #   not implemented by defaulting to 1.0
    # Results:
    #  A wavelength array is included in the array of the extracted spectra.
    def __init__(self, spex, wvs, window=1.0):

        numsp = spex.shape[2]
        numel = spex.shape[0]
        print (numsp)
        loop_over = range(numsp)
        self.spex = spex
        self.wvs  = wvs
        self.pix  = range(numel)
        self.warr = np.zeros((numel,numsp)).copy()
        if len(wvs) >= 4:
            self.fitparams = np.zeros((3,numsp)).copy()
        else:
            self.fitparams = np.zeros((2,numsp)).copy()
        self.i = None
        for self.i in loop_over:
            fig = plt.figure()
            self.ax = plt.gca()
            # the width of the median window taken at each point
            self.winwidth = window/2.0
            
            self.ax.plot(self.spex[:,4,self.i],'k-',label='spectrum')
            plt.title('Wavelength Calibration: Spectrum Number '+str(self.i+1))
            self.ax.text(100,max(spex[:,4,self.i]),'(1) define data points,')
            self.ax.text(100,0.95*max(spex[:,4,self.i]),'R-mouse to remove,')
            self.ax.text(100,0.9*max(spex[:,4,self.i]),'and "R" to reset')
            self.ax.text(100,0.85*max(spex[:,4,self.i]),'(2) <Enter>: solve')
            self.ax.text(100,0.8*max(spex[:,4,self.i]),'(3) <Ctrl-W>: Close/save')
            
            # Connect the different functions to the different events
            fig.canvas.mpl_connect('key_press_event',self.ontype)
            fig.canvas.mpl_connect('button_press_event',self.onclick)
            fig.canvas.mpl_connect('pick_event',self.onpick)
            plt.show() # show the window
            
            self.spex[:,0,self.i] = self.warr[:,self.i]

    # ONCLICK:
    #  When the plot is left-clicked, the nearest x-coordinate point is found.
    #  The 'feel-radius' (picker) set to 5 points so that the spectrum points
    #   feel it when they are clicked.
    def onclick(self, event):
        toolbar = plt.get_current_fig_manager().toolbar
        if event.button==1 and toolbar.mode=='':
            window = 1.0
            y = self.spex[int(np.rint(event.xdata)),4,self.i]
            self.ax.plot(np.rint(event.xdata),y,'rs',ms=10,picker=5,label='wv_pnt')
        plt.draw()

    # ONPICK:
    #  When the user right-clicks on a chosen point, remove it
    def onpick(self, event):
        if event.mouseevent.button==3:
            if hasattr(event.artist,'get_label') and event.artist.get_label()=='wv_pnt':
                event.artist.remove()

    # ONTYPE:
    #  Type <ENTER>: Performs the wavelength calibration and prints the 
    #   slope and y-intercept to the terminal
    #  Type 'R': Re-set the selected points and begin wavelength calibration
    #   over again
    def ontype(self, event):
        if event.key=='enter':
            wv_pnt_coord = []
            for artist in self.ax.get_children():
                if hasattr(artist,'get_label') and artist.get_label()=='wv_pnt':
                    wv_pnt_coord.append(artist.get_data())
                elif hasattr(artist,'get_label') and artist.get_label()=='wavelengths':
                    artist.remove()
            wv_pnt_coord = np.array(wv_pnt_coord)[...,0]
            sort_array = np.argsort(wv_pnt_coord[:,0])
            x,y = wv_pnt_coord[sort_array].T
            #print x
            # Choose linear or quadratic fit to wavelengths
            if len(self.wvs) >= 4:
                params = curve_fit(self.quad,x,self.wvs,p0=[0.0,0.0,0.0])
                self.fitparams[0,self.i] = params[0][0]
                self.fitparams[1,self.i] = params[0][1]
                self.fitparams[2,self.i] = params[0][2]
                print ('a = ',params[0][0],', b = ',params[0][1],' and c = ',params[0][2])
            else:
                params = curve_fit(self.line,x,self.wvs,p0=[0.0,0.0])
                self.fitparams[0,self.i] = params[0][0]
                self.fitparams[1,self.i] = params[0][1]
                print ('m = ',params[0][0],', and b = ',params[0][1])
            print (' ')
            for j in self.pix:
                if len(self.wvs) >= 4:
                    self.warr[j,self.i] = self.quad(self.pix[j],params[0][0],params[0][1],params[0][2])
                    #self.warr[j,self.i] = params[0][0] * self.pix[j]**2 + params[0][1] * self.pix[j] + params[0][2]
                else:
                    self.warr[j,self.i] = self.line(self.pix[j],params[0][0],params[0][1])
                    #self.warr[j,self.i] = params[0][0] * self.pix[j] + params[0][1]

        # when the user hits 'r': clear the axes and plot the original spectrum
        elif event.key=='r':
            self.continuum = None
            self.ax.cla()
            self.ax.plot(self.spex[:,4,self.i],'k-',label='spectrum')
            plt.title('Wavelength Calibration: Spectrum Number '+str(self.i+1))
            self.ax.text(100,max(self.spex[:,4,self.i]),'(1) define data points,')
            self.ax.text(100,0.95*max(self.spex[:,4,self.i]),'R-mouse to remove,')
            self.ax.text(100,0.9*max(self.spex[:,4,self.i]),'and "R" to reset')
            self.ax.text(100,0.85*max(self.spex[:,4,self.i]),'(2) <Enter>: solve')
            self.ax.text(100,0.8*max(self.spex[:,4,self.i]),'(3) <Ctrl-W>: Close/save')
            plt.draw()


    # Function line: y = mx + b, called by ONTYPE
    def line(self,x, m, b):
        return m*x + b

    # Function quad: y = ax^2 + bx + c, called by ONTPYE
    def quad(self,x,a,b,c):
        return a*x**2 + b*x + c
