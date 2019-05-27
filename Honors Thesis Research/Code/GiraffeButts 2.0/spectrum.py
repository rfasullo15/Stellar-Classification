'''
The purpose of a spectrum object is to maintain the calculated values for a given spectrum.

History:

6/25/2018: Class created. Spectrum objects can calculate the location of their H absorption lines

7/2/2018: isRectified, calWaves, and recWaves added.

@rfasullo

'''
import numpy as np
import copy

class Spectrum:

    def __init__(self, name):

        self.namaste = name

        self.wv = []                      # calibrated wavelengths
        self.raw = []                    # raw 
        self.rms = []                    # raw minus sky
        self.rectified = []           # rectified spectrum
        self.waves = []                # wavelengths
        self.snr = []                    #  signal to noise ratio


    def setVals(self, wv, raw, rms, rectified, waves, snr):
        self.wv = wv
        self.raw = raw
        self.rectified = rectified
        self.waves = waves
        self.snr = snr

    def __repr__(self):
        return ("Spectrum for " + self.namaste)
                
        


