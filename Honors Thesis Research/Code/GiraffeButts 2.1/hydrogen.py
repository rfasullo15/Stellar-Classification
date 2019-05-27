'''
9/28/2018: class created. An instance of a hydrogen object contains the strength of the line and the lorentzian fit of the line.
                    A hydrogen object can calculate the its own strength and its lorenzian fit.
10/1/2018:  initial configuration of class completed.
10/4/2018: Lorentz fit successfully completed! It looks suuuuper good!!!

'''

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import math

class Hydrogen:

    def __init__(self, center, hydrodf, index, rightIndex, leftIndex, name = None):
        self.name = name
        self.center= center                                                            #Hydrogen line center, defined explicitly in spectrum.py
        self.index = index
        self.rightIndex = rightIndex
        self.leftIndex = leftIndex
        self.hydrodf= pd.DataFrame.from_dict(hydrodf) #a subset of the main df in s_type
        self.inEmission = False
        self.setValues()

    def setValues(self):
        self.length = self.hydrodf.shape[0]
        #print(self.name)

        #print(self.hydrodf)
        #self.peicewise()
        
        
        self.contLine = self.findContLine()
        self.strength = self.lineStrength()
        #self.leftCont = self.findAvgCont("L")
        #self.rightCont = self.findAvgCont("R")
        self.newCenterIdx = self.getNewIndex()
        try:
            self.poptL, self.pcovL = curve_fit(self.lorentzFit, self.hydrodf["wv"][0:self.newCenterIdx].values, self.hydrodf["local"][0:self.newCenterIdx].values, p0 = [1, self.center, 1, self.strength])
        except:
            print("ERROR LEFT at " + self.name)
            #self.poptL = 1, self.center, 1, self.strength   #FWHM, center, continuum, strength
            self.poptL = 0,0,0,0

        try:
            self.poptR, self.pcovR = curve_fit(self.lorentzFit, self.hydrodf["wv"][self.newCenterIdx:self.length].values, self.hydrodf["local"][self.newCenterIdx:self.length].values, p0 = [1, self.center, 1, self.strength])
        except:
            print("ERROR RIGHT at " + self.name)
            #self.poptR= 1,self.center, 1, self.strength
            self.poptR = 0,0,0,0

        
#Averaging, standard, ??????????????????????, remove those rows, remove the rows for the whole day 


    '''
    Removes the metal lines from the continuum, creating a peicewise version of the hydrogen line that should be easier to fit
    
    def peicewise(self): 
        linelength = 5
        goalslope = -.01

        idxR= self.length-1
        idxL = idxR - linelength

        print(idxR)
        print(idxL)
        
        #while idxL > -1:
        while idxL> -1:
            x1 = self.hydrodf["wv"][idxR]
            #print("X1")
            #print(x1)
            y1 = self.hydrodf["local"][idxR]
            x2 = self.hydrodf["wv"][idxL]
            #print("X2")
            #print(x2)

            print("Slope")
            y2 = self.hydrodf["local"][idxL]

            slope = (y2 - y1)/(x2-x1)
            print(slope)
            
            if(slope < goalslope):
                print("Metal line???")
                print(self.hydrodf["wv"][idxR])
                #print(idxL)

            idxR = idxL
            idxL = idxR - linelength
            #print(idxR)
            #print(idxL)
            #if (idxL < 0):
             #   idxL= 0

    '''
            
        
    '''
    finds the index for where the center of the line is
    '''
    def getNewIndex(self):
        index = 0
        while index<self.hydrodf["wv"].shape[0] and self.hydrodf["wv"][index] - self.center > 1:
            index +=1

        return index
        
    '''
    The Lorentzian curve being fit to a hydrogren line wing. Computes line center, FWHM, area
    '''
    def lorentzFit(self, x, gam, avg, cont, strength):
        return (-strength/math.pi) * ((0.5*gam)/((x-avg)**2 + (0.5*gam)**2)) + cont
    
    '''
    Calculates the projected average value of the continuum on that side. Used for fitting the lorentz curve correctly
    '''
    def findAvgCont(self, side):
        if side == "R":
            lst = self.hydrodf["wv"][0:self.hydrodf.shape[0]/2]*self.contLine[0] + self.contLine[1]
            return sum(lst)/len(lst)
        else:
            lst = self.hydrodf["wv"][self.hydrodf.shape[0]/2:self.length]*self.contLine[0] +self.contLine[1]
            return sum(lst)/len(lst)
            
        
    '''
    Finds the slope and y intercept of the line representing the continuum
    '''
    def findContLine(self):
        #Formula y= mx + b

        slope = (self.hydrodf["local"][0] - self.hydrodf["local"][self.length-1])/(self.hydrodf["wv"][0] - self.hydrodf["wv"][self.length -1])
        b = self.hydrodf["local"][0] - slope*self.hydrodf["wv"][0]

        return (slope,b)

    '''
    determines the rough strength of the given line. If the strength is negative or close to 0 it indicates a large amount of emission
    '''
    def lineStrength(self):
            xvals = self.hydrodf["wv"]
            y1 = self.hydrodf["local"]
            y2 = self.contLine[0]*xvals + self.contLine[1]

            strength = 0

            '''
            Sums up each individual trapezoid between the right index and left index
            '''
            count = 0
            while count<self.length-1:
                h = abs(xvals[count + 1] - xvals[count])
                a = y2[count+1] - y1[count+1]
                b = y2[count] - y1[count]
                strength  += (a +b) *h *0.5 #area of the trapezoid
                count+=1

            return strength
    
