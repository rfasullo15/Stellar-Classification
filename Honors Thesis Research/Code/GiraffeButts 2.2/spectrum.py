'''
The purpose of a spectrum object is to maintain the calculated values for a given spectrum.

History:

6/25/2018: Class created. Spectrum objects can calculate the location of their H absorption lines

7/2/2018: isRectified, calWaves, and recWaves added.

9/28/2018: Changed up everything. Spectrum now has 3 member variables: df, hydros, and sections. It has two method stubs: localContinuum and genHydros. See comments for descriptions of variables and methods.

10/11/2018: H9 is not present for many of the strong candidates and so it was decided to omit it completely.

1/25/2019: Randomly perturbing by 5% instead of using the signal to noise ratio to determine sigma.
@rfasullo

'''

import hydrogen
import pandas as pd
import numpy as np
import math
class Spectrum:

    def __init__(self, df, name = None, classification = "-"):
        #print(name)
        self.name = name
        self.classification = classification
        self.df = df             #6x2048 table of spectrum values. "wv", "rms", "snr". The column "local" will be added at a later time.

        self.max = self.df["wv"][0]
        self.min = self.df["wv"][2047]
        #pd.set_option("display.max_rows", 2048)

        self.section = [(self.df["wv"][2047], 3919), (3920, 4050), (4051,4215), (4216, 4700), (4701,self.df["wv"][0])]        #sections used to create the new local column.
        self.localContinuum()

        perc_change = 0.05
        self.df["Sigma"] = self.df["rms"]*perc_change
        #print(self.df)

        self.hydros = []     #collection of 6 hydrogen objects
        self.genHydros()

        
        


    '''
    localcontinuum will find the specified points and calculate the slope between two adjacent points. After the slope has been calculated
    the section of rms will be divided through for each section to determine a local continuum and plot the newly rectified spectrum. Its gonna look super weird.
    '''
    def localContinuum(self):

        section1 = self.generateSection(self.section[0][0], self.section[0][1], index1 = self.df["rms"].shape[0])
        section2 = self.generateSection(self.section[1][0], self.section[1][1])
        section3 = self.generateSection(self.section[2][0], self.section[2][1])
        section4 = self.generateSection(self.section[3][0], self.section[3][1])
        section5 = self.generateSection(self.section[4][0], self.section[4][1], index2 = 1) #Not the real index, but using 1 as a flag that this is the end                  
        
        self.df["local"] = section5.append(section4).append(section3).append(section2).append(section1)

    '''
    given two wavelengths (x1, x2) generateSection will generate the locally rectified version of that section. Option to put in a set index for the first index and the last index of the
    master rms list.
    '''
    def generateSection(self, x1, x2, index1 = 0, index2 = 0):
        
        if index1 !=0 and index2 == 0:   #get the last point in rms
            x1, y1, dummy = self.selectpeaks(x1)
            x2, y2, index2 = self.selectpeaks(x2)
            
        elif index1 == 0 and index2 != 0: #get the first point in rms
            x1, y1, index1 = self.selectpeaks(x1)
            x2, y2, dummy = self.selectpeaks(x2)
            index2 = 0
            
        else:     #Any of the middle points
            x1, y1, index1 = self.selectpeaks(x1)
            x2, y2, index2 = self.selectpeaks(x2)
            
        point1 = (x1, y1)
        point2 = (x2, y2)

        m, b = self.findLine(point1, point2) #Find the equation of the line
        
        section = self.computeNewPoint(self.df["rms"][index2:index1], self.df["wv"][index2:index1], m, b)

        return section

    '''
    select the hydrogen linessta
    '''
    def selectpeaks(self, val):

        index = 0
        while index<self.df["wv"].shape[0] -1 and abs(self.df["wv"][index] - val ) > 1:
            index +=1
            
        y = self.df["rms"].iloc[index]
        x = self.df["wv"].iloc[index]

        return (x,y, index)
        

    '''
    will find the new rectified point based off the function of the line. Divides the unrectified y value (y0) by the line on the point
    '''
    def computeNewPoint(self, y0, x, slope, b):
        return y0/(slope*x + b)      #original y divided by the y value on the line at that x value
    
    '''
    given two points this will find the slope and y intercept of the line 
    '''
    def findLine(self, point1, point2):
        #Formula y= mx + b

        slope = (point2[1] - point1[1])/(point2[0] - point1[0])
        b = point1[1] - slope*point1[0]

        return (slope, b)

    '''
    genHydro  generates the 5 hydrogen lines for this spectrum
    '''
    def genHydros(self, lines = [3889, 3970, 4101, 4340, 4861]):          #H9: 3835
        babystep = 50
        
       
        self.genSingleHydro(lines[0], babystep, name = "H8")
        self.genSingleHydro(lines[1], babystep, name = "H epsilon")
        self.genSingleHydro(lines[2], step= 80, name = "H delta")
        self.genSingleHydro(lines[3], step = 90, name = "H gamma")
        self.genSingleHydro(lines[4], step = 90, name = "H beta")


    def genSingleHydro(self, center, step, name = None):
        rightIndex, leftIndex, centerIndex= self.findHydroCont(center, step)
        hydrodf = {"wv":  self.df["wv"][rightIndex:leftIndex].values, "rms": self.df["rms"][rightIndex:leftIndex].values,"snr": self.df["snr"][rightIndex:leftIndex].values, "local": self.df["local"][rightIndex:leftIndex].values}
        self.hydros.append(hydrogen.Hydrogen(center, hydrodf, centerIndex, name = name, rightIndex = rightIndex, leftIndex = leftIndex))

        
    def findHydroCont(self, val, step):

        x, y, index = self.selectpeaks(val)
        
        buffet  = 5
        
        '''
        Right wing. This indexing may seem confusing, but the spectrum is plotted backwards to how it is stored in the array.
        '''
        if (index - step < 0):
            rightX = self.df["wv"][0]
            rightY = self.df["local"][0]
            rightIndex = 0
        else:
            rightX = self.df["wv"][index-step]
            rightY = np.median(self.df["local"].iloc[index-step-buffet: index-step+buffet+1])
            rightIndex = index-step

        '''
        Left wing
        '''
        if (index + step >2047):
            leftX = self.df["wv"][2047]
            leftY = self.df["local"][2047]
            leftIndex = 2047
        else:
            leftX = self.df["wv"][index+step]
            leftY = np.median(self.df["local"].iloc[index+step-buffet: index+step+buffet+1])
            leftIndex = index + step 
        
        return (rightIndex, leftIndex, index)
    

    def __repr__(self):
        return ("Spectrum for " + self.name)
                
        


