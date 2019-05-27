'''
8-30-2018 RBF: Created file.
9-11-2018 RBF: New Version to created. Cleaned up the code so only the essentials are included.
9-13-2018 RBF: Peak location successfully implemented.

This will create a pandas data frame that will house all of the values for the respective spectra.
'''

import pandas as pd
import numpy as np
import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#import os,glob
import spectrum
#import pickle
import os.path
#import bisect
import math
from scipy.optimize import curve_fit


class classification(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent.root)
        self.rent = parent

        winHeight = 600
        specwidth = 800

        specframe = tk.Frame(self, height = winHeight, width = specwidth)

        fig = plt.figure(figsize = (19, 9))
        self.ax = fig.gca()

        self.winwidth = 1/2

        self.canv = FigureCanvasTkAgg(fig, master = specframe)
        self.canv.get_tk_widget().pack(side = tk.TOP, fill = 'both', expand = 1)

        self.setFigure()

        toolframe = tk.Frame(specframe)
        self.toolbar = NavigationToolbar2TkAgg(self.canv, toolframe)

        toolframe.pack(side = tk.BOTTOM)
        specframe.grid(column = 0, row = 0)

        #self.canv.mpl_connect('key_press_event', self.ontype)
        #self.canv.mpl_connect('button_press_event', self.onclick)
        #self.canv.mpl_connect('pick_event', self.onpick)

        plt.close()
        
        self.spex =''
        headers = ["H9 3835", "H8 3889", "Hep 3970", "Hdel 4101", "Hgam 4340", "Hb 4861", "H9 wing", "H8 wing", "Hdel wing", "Hgram wing", "Hb wing", "He I 4009", "He I 4026", "He I 4144", "He I 4387", "He I 4387", "He I 4471", "He I 4121", "He I 4922", \
                            "He I 4714", "He II 4200", "He II 4541", "Si IV 4089", "Si IV 4116", "Si II 4128", "Si II 4130", "Si II 4201", "Si II 3856", "Si II 3862", "Si II 4002", "Si II 4028", "Si II 4076", "C II 4267", "Si III 4552", "Mg II 4481", "Mg II 3984", \
                            "Ca II K 3984", "Mn I 4030", "Fe I 4046", "Fe I 4271", "Fe I 4383", "Ca I 4226", "Cr II 4172", "Cr II 4111", "Cr II 3866", "Sr II 4216", "Mn II 4136", "Mn II 4206", "Mn II 4252", "Mn II 4259", "Eu II 4205", "Eu 4130", "Fe II 4172", \
                             "Fe II 4233", "Fe II 4395", "Ti II 4179", "Ti II 4400", "N II 3995", "3905-4050", "4051-4215", "4216-4700", "4701-4950"]
        #df  = pd.DataFrame(np.zeros(62,1)) #, index = ["I am a spectrum"], columns = headers )

        zero_dat = np.zeros(shape = (1,len(headers)))
        df = pd.DataFrame(zero_dat, index = ["Poops"], columns = headers)

    def setFigure(self):
        folder_path = "C:\\Users\\90rfa\\Dropbox\\Honors Thesis Research\\Code\\Testing Data\\"
        self.df = pd.read_csv(folder_path+"HD172167_20180703.txt", delim_whitespace = True)

        self.ax.clear()
        self.ax.plot(self.df["wv"], self.df["rms"], "k-")

        self.hydro()

    ''' 
    hydro selects the points for all of the hydrogen balmer series absorption peaks
    '''
    def hydro(self):
        self.selectpeaks(3835, False)
        self.selectpeaks(3889, False)
        self.selectpeaks(3970, False)
        self.selectpeaks(4101, False)
        self.garbage = self.selectpeaks(4340, False)
        self.selectpeaks(4861, False)

        
    def selectpeaks(self, val, isCon):

        wv = np.around(np.array(self.df["wv"]), 0).astype(int)
        
        indeces = np.where(wv == val)                                                           #All of the indexes where the integer list equals the wavelength we want
        possibles = self.df["rms"].iloc[indeces[0]]                                         #Get the associated rows from rms
        y = possibles.min()                                                                             #Get the minimum of the selected rows from rms
        x = self.df["wv"].iloc[possibles.idxmin()]                                          #Index of the location of the minimum in rms
        
        #print(x)
        #print(y)
        if (isCon):
            self.ax.plot(x,y, 'go', ms = 5, picker = 5, label = "wv")
        else:
            self.ax.plot(x,y,'rs',ms=10,picker=5,label='wv_pnt')           # Draw the box
        return (x,y, indeces[0][0])

    '''
    localcontinuum will find the specified points and calculate the slope between two adjacent points. After the slope has been calculated
    the section of rms will be divided through for each section to determine a local continuum and plot the newly rectified spectrum. Its gonna look super weird.
    '''
    def localcontinuum(self):
        
        '''
        selecting the continuum points
        '''

        section1 = self.generateSection(3821, 3919, index1 = self.df["rms"].shape[0])
        section2 = self.generateSection(3920, 4050)
        section3 = self.generateSection(4051, 4215)
        section4 = self.generateSection(4216, 4700)
        section5 = self.generateSection(4701, 4943, index2 = 1) #Not the real index, but using 1 as a flag that this is the end                  
        
        self.df["local"] = section5.append(section4).append(section3).append(section2).append(section1)

        self.ax.clear()
        self.ax.plot(self.df["wv"], self.df["local"], "k-")
        self.canv.draw()

    def unrectify(self):
        
        self.ax.clear()
        self.ax.plot(self.df["wv"], self.df["rms"], "k-")
        self.hydro()
        self.canv.draw()

    '''
    given two points this will find the slope and y intercept of the line 
    '''
    def findLine(self, point1, point2):
        #Formula y= mx + b

        slope = (point2[1] - point1[1])/(point2[0] - point1[0])
        b = point1[1] - slope*point1[0]

        return (slope, b)

    '''
    will find the new rectified point based off the function of the line. Divides the unrectified y value (y0) by the line on the point
    '''
    def computeNewPoint(self, y0, x, slope, b):
        return y0/(slope*x + b)      #original y divided by the y value on the line at that x value

    '''
    given two wavelengths (x1, x2) generateSection will generate the locally rectified version of that section. Option to put in a set index for the first index and the last index of the
    master rms list.
    '''
    def generateSection(self, x1, x2, index1 = 0, index2 = 0):
        
        if index1 !=0 and index2 == 0:   #get the last point in rms
            x1, y1, dummy = self.selectpeaks(x1, True)
            x2, y2, index2 = self.selectpeaks(x2, True)
            
        elif index1 == 0 and index2 != 0: #get the first point in rms
            x1, y1, index1 = self.selectpeaks(x1, True)
            x2, y2, dummy = self.selectpeaks(x2, True)
            index2 = 0
            
        else:     #Any of the middle points
            x1, y1, index1 = self.selectpeaks(x1, True)
            x2, y2, index2 = self.selectpeaks(x2, True)
            
        point1 = (x1, y1)
        point2 = (x2, y2)

        m, b = self.findLine(point1, point2) #Find the equation of the line
        
        section = self.computeNewPoint(self.df["rms"][index2:index1], self.df["wv"][index2:index1], m, b)

        return section

    '''
    Does both lorentz fits for the first hydrogen lines and displays it in a separate window.
    '''
    def createExampleLorentz(self):
        babystep = 50
        bigstep = 80
        rightIndex, leftIndex, m, b = self.findHydroCont(4340, bigstep)
        strength = self.lineStrength(rightIndex, leftIndex, m, b)

        popt, pcov = curve_fit(self.lorentzCurve, self.df["wv"][rightIndex:self.garbage[2]].values, self.df["local"][rightIndex:self.garbage[2]].values)
        print(popt)
        plt.plot(self.df["wv"][rightIndex:self.garbage[2]], self.lorentzCurve(self.df["wv"][rightIndex:self.garbage[2]], popt[0], popt[1], popt[2]))
        plt.plot(self.df["wv"][rightIndex:leftIndex], self.df["local"][rightIndex:leftIndex])

        plt.show()
            
        
        
    '''
    Does both lorentz fits for all 6 hydrogen lines (for a total of 12 lorentz functions) and displays them simultaneously
    '''
    def createAllLorentz(self):
        babystep = 50
        bigstep = 80
        
        r, l, m,b = self.findHydroCont(3835, babystep)
        self.lineStrength(r,l,m,b)
        r, l, m,b =self.findHydroCont(3889, babystep)
        self.lineStrength(r,l,m,b)
        r, l, m,b =self.findHydroCont(3970, babystep)
        self.lineStrength(r,l,m,b)
        r, l, m,b =self.findHydroCont(4101, bigstep)
        self.lineStrength(r,l,m,b)
        r, l, m,b =self.findHydroCont(4340, bigstep)
        self.lineStrength(r,l,m,b)
        r, l, m,b =self.findHydroCont(4861, bigstep)
        self.lineStrength(r,l,m,b)

        
    '''
    The Lorentzian curve being fit to a hydrogren line wing. Computes line center, FWHM, area
    '''
    def lorentzCurve(self, x,  gam, strength, avg = 4340):
        return (-strength/math.pi) * ((0.5*gam)/((x-avg)**2 + (0.5*gam)**2)) +1

    def findHydroCont(self, val, step):
        buffet = 5
        wv = np.around(np.array(self.df["wv"]), 0).astype(int)
        
        indeces = np.where(wv == val)                                                           #All of the indexes where the integer list equals the wavelength we want
        possibles = self.df["local"].iloc[indeces[0]]                                         #Get the associated rows from rms
        y = possibles.min()                                                                             #Get the minimum of the selected rows from rms
        x = self.df["wv"].iloc[possibles.idxmin()]                                          #Index of the location of the minimum in rms

        index = possibles.idxmin()
        
        self.ax.plot(x,y, 'rs', ms = 5, picker = 5, label = "wv")


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

        self.ax.plot(rightX, rightY, "go", ms = 5, picker = 5, label = "cont")

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
            
        self.ax.plot(leftX, leftY, "go", ms = 5, picker = 5, label = "cont")

        m, b = self.findLine((rightX, rightY), (leftX, leftY))
        xvals = self.df["wv"][rightIndex:leftIndex]
        self.ax.plot(xvals, b + m *xvals, "-")

        self.canv.draw()
        
        return (rightIndex, leftIndex, m, b)

    def lineStrength(self, rightIndex, leftIndex, m, b):
        xvals = self.df["wv"][rightIndex:leftIndex]
        y1 = self.df["local"][rightIndex:leftIndex]
        y2 = m*xvals + b

        self.ax.fill_between(xvals, y1, y2)

        self.canv.draw()

        strength = 0

        '''
        Sums up each individual trapezoid between the right index and left index
        '''
        count = rightIndex
        while count<leftIndex-1:
            h = abs(xvals[count + 1] - xvals[count])
            a = y2[count+1] - y1[count+1]
            b = y2[count] - y1[count]
            strength  += (a +b) *h *0.5 #area of the trapezoid
            count+=1

        return strength
        
        

        







        
