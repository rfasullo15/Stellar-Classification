#!/usr/bin/python
#
# spec_contrect_spline.py
#
# A class that provides a GUI for rectifying the spectrum or else allows for
#  automated continuum rectification.
#
# Class RECT:
#
#  __INIT__: The main program
#  ONCLICK: finds the nearest x-coordinate point clicked
#  ONPICK: Mouse right-click removes a point defined using ONCLICK
#  ONTYPE: Three options
#   <ENTER>: Perform the continuum rectification
#   "D": Divide the spectrum by the calculated continuum and plot the rectified
#        spectrum
#   "R": Resets the clicked data points -- allows you to re-do contrect
#  CONTREGS: For automated continuum rectification, the continuum regions that
#   will be used
#  QUAD, CUBIC, QUARTIC, QUINTIC, SEXTIC, SEPTIC, OCTIC, NONIC, DECIC: different
#   powers for the continuum fit --> Obsolete with a cubic spline
#
# Dependencies:
#  
#  pylab
#  numpy
#  scipy
#  sys
#  os
#  time
#
# History:
#  DGW, 13 May 2016: Edited from the original, specnorm.py
#  DGW, 17 May 2016: Code is commented
#  DGW, 15 July 2016: Polynomial fits have been abandoned in favor of a cubic spline fit. 
#                     INIT calls splrep,splev. CONTREGS solves for the average
#                     wavelength and flux in each of the continuum region windows.
#
#  RBF, 26 June 2018: Created new gui for continuum rectification
#  RBF, 3 July 2018: Plots show side by side for direct comparison of iterations of the rectified spectrum
#
#
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splrep,splev
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import Tkinter as tk
from matplotlib.backend_bases import key_press_handler
import sys
import os
import time

class rect:

    # __INIT__
    # Inputs:
    #  SPEX: The array of spectra returned from SPEC_EXTRACT, SPEC_WAVECAL
    #  WINDOW: When choosing continuum points, find the median value of the 
    #   continuum within a certain wavelength range around the clicked point.
    #   Default is 10.
    #  FILENAME: If you want to write out the spectrum (not currently 
    #   implemented), the name of the output file
    #  AUTO: Auto-rectify? Default is 'no'.
    #  POLY: What order polynomial do you want to fit to the continuum?
    #   Options are from quadratic (2) to decic (10)
    # Results:
    #  Continuum-rectified spectrum included in SPEX
    def __init__(self, spex,  srcnames, window=10.0, filename=None,auto='no',poly=9):

        winHeight = 600
        newfont = ("Helvetica, 15")

        self.root = tk.Tk()
        self.root.title("Continuum Rectification")

        infoWidth = 200
        infoframe = tk.Frame (self.root, width = infoWidth, height= winHeight)

        instructions = "Instructions: \n \t1) Define data points \n \t2) <Enter>: Solve \n \t3) <D> View rectified spectrum \n \t4) <Ctrl-W>: Close/save"
        instlabel = tk.Label(infoframe, text = instructions, justify = tk.LEFT)
        instlabel.grid(row= 0, column = 0, pady = 10)

        shortcuts = "Shortcuts: \n \tRight-click to remove points \n \t<R> to reset"
        shortlabel = tk.Label(infoframe, text = shortcuts, justify = tk.LEFT)
        shortlabel.grid(row= 1, column = 0, pady = 10)

        buttframe = tk.Frame(infoframe, width = infoWidth, height = 100)

        rectbutt = tk.Button(buttframe, text = "Rectify", command = self.rect_button)
        rectbutt.pack(side = tk.LEFT, padx = 10)
        resetbutt = tk.Button(buttframe, text = "Reset", command = self.reset_button)
        resetbutt.pack(side = tk.LEFT, padx = 10)

        buttframe.grid(row = 2, column = 0, pady = 10)

        listframe = tk.Frame(infoframe, width = infoWidth, height = 100)

        scroller = tk.Scrollbar(listframe)

        self.imglist = tk.Listbox(listframe, width = 30)
        self.imglist.pack(side = tk.LEFT, fill= 'y')

        scroller.configure(command = self.imglist.yview)
        scroller.pack(side = tk.LEFT, fill = 'y')
        
        for name in srcnames: self.imglist.insert(tk.END, name)
        self.imglist.selection_set(0)
        self.imglist.bind("<<ListboxSelect>>", self.on_select)

        listframe.grid(row = 3, column = 0, pady = 10)

        finbutt = tk.Button(infoframe, text = "Finish", command = self.fin_button)
        finbutt.grid(row = 4, column = 0, pady = 10)

        infoframe. grid(column = 1, row = 0)

        specwidth = 550

        specframe = tk.Frame(self.root, height = winHeight, width = specwidth, bd = 1, relief = tk.SUNKEN)

        #Create the figure we want on the canvas 

        self.currspec = 0
        
        fig = plt.figure(figsize = (12, 8))
        self.ax = fig.add_subplot(211)
        plt.title("Continuum Rectification: Spectrum for: " + str(srcnames[self.currspec]))

        numsp = spex.shape[2]
        numel = spex.shape[0]
        self.spex = spex
        self.continuum = None
        self.cfunc = None
        self.currspec = 0

        self.ax.plot(self.spex[:,0,self.currspec],self.spex[:,2,self.currspec],'k-',label='spectrum')
        self.filename = filename

        self.ax2 = fig.add_subplot(212)
        self.ax2.plot(self.spex[:,0,self.currspec], self.spex[:, 3, self.currspec], 'k-', label = 'rectified')

        #self.spex[:,3,self.currspec] = self.spex[:,2,self.currspec]/self.continuum
        
        # the width of the median window taken at each point
        self.winwidth = window/2.0

        self.canv = FigureCanvasTkAgg(fig, master = specframe)
        self.canv.get_tk_widget().pack(side = tk.TOP, fill = "both", expand = 1)

        # Connect the different functions to the different events
        fig.canvas.mpl_connect('key_press_event',self.ontype)
        fig.canvas.mpl_connect('button_press_event',self.onclick)
        fig.canvas.mpl_connect('pick_event',self.onpick)
    
        self.canv.draw()
        
        toolframe = tk.Frame(specframe)
        self.toolbar = NavigationToolbar2TkAgg(self.canv, toolframe)

        toolframe.pack(side= tk.BOTTOM)
        specframe.grid(column = 0, row= 0)

        self.canv.mpl_connect("key_press_event", self.ontype)
        self.canv.mpl_connect("button_press_event", self.onclick)
        self.canv.mpl_connect("pick_event", self.onpick)

        self.root.mainloop()
        plt.close()
        

    def rect_button(self):
        if self.continuum is not None:
            self.ax2.cla()
            self.ax2.plot(self.spex[:,0,self.currspec],self.spex[:,2,self.currspec]/self.continuum,'k-',label='rectified')
            self.canv.draw()

    def reset_button(self):
        self.continuum = None
        self.ax.cla()
        self.ax.plot(self.spex[:,0,self.currspec],self.spex[:,2,self.currspec],'k-')
        self.ax2.cla()
        self.ax2.plot(self.spex[:,0, self.currspec], self.spex[:, 3, self.currspec], 'k-', label = 'rectified')
        self.canv.draw()

    def fin_button(self):
        self.root.destroy()
        plt.close()

    def on_select(self, event):
        self.currspec = event.widget.curselection()[0]
        
        
    # ONCLICK: For a left-click in the GUI, compute the median value of the 
    #  x-coordinate spectrum in a specified window. The 'feel-radius' (picker)
    #  is set to 5 so that the points 'feel' it when they are clicked.
    def onclick(self, event):
        if event.button==1 and self.toolbar.mode=='':
            window = ((event.xdata-self.winwidth)<=self.spex[:,0,self.currspec]) &\
                      (self.spex[:,0,self.currspec]<=(event.xdata+self.winwidth))
            y = np.median(self.spex[window,2,self.currspec])
            self.ax.plot(event.xdata,y,'rs',ms=10,picker=5,label='cont_pnt')
        self.canv.draw()

    # ONPICK: For a right-click, remove the continuum point.
    def onpick(self, event):
        if event.mouseevent.button==3:
            if hasattr(event.artist,'get_label') and event.artist.get_label()=='cont_pnt':
                event.artist.remove()

    # ONTYPE: Three options
    #  <ENTER>: Fit the continuum
    #  "D": Divide spectrum by continuum (this is rectification)
    #  "R": Reset chosen continuum points and re-do selection/rectification
    def ontype(self, event):
        if event.key=='enter':
            cont_pnt_coord = []
            for artist in self.ax.get_children():
                if hasattr(artist,'get_label') and artist.get_label()=='cont_pnt':
                    cont_pnt_coord.append(artist.get_data())
                elif hasattr(artist,'get_label') and artist.get_label()=='continuum':
                    artist.remove()
            cont_pnt_coord = np.array(cont_pnt_coord)[...,0]
            sort_array = np.argsort(cont_pnt_coord[:,0])
            x,y = cont_pnt_coord[sort_array].T
            spline = splrep(x,y,k=3)
            self.continuum = splev(self.spex[:,0,self.currspec],spline)
            self.cfunc = lambda w: splev(w, spline)
            self.ax.plot(self.spex[:,0,self.currspec],self.continuum,'r-',lw=2,label='continuum')
            self.canv.draw()

        elif event.key=='d':
            self.rect_button()

        elif event.key=='r':
            self.reset_button()

        # when the user hits 'w': if the normalised spectrum exists, write it to a
        # file.
        #elif event.key=='w':
        #    for artist in self.ax.get_children():
        #        if hasattr(artist,'get_label') and artist.get_label()=='normalised':
        #            data = np.array(artist.get_data())
        #            if self.filename == None:
        #                self.filename = 'normalised_spec.flm'
        #            np.savetxt(os.path.splitext(self.filename)[0]+'.nspec',data.T)
        #            print('Saved to file:',self.filename)
        #            break
        #plt.draw()

    # CONTREGS: Defined continuum regions
# 2016-07-05, POSSIBLE NEW, DIFFERENT CONTREGS: DEFINE GOOD CONTINUUM WAVELENGTHS, SET FLUX TO MEDIAN OF TEN OR ELEVEN POINTS SURROUNDING EACH WAVELENGTH. SHOULD WORK BETTER FOR STEEP CONTINUA THAN THE CURRENT PROPOSED CHANGE TO THE IMPLEMENTATION.
    def contregs(self,specin):
        wvin = specin[:,0,self.currspec]
        fxin = specin[:,2,self.currspec]
        # The continuum regions of the spectrum:
        # 3806 - 3816
        idx3806 = np.array(np.nonzero((wvin >= 3806) & 
                                      (wvin <= 3816))).reshape(-1).tolist()
        if idx3806:
            wv3806  = wvin[int(np.floor(np.mean(idx3806)))]
            fx3806  = np.median(fxin[idx3806])
        else:
            wv3806 = 0.0
            fx3806 = 0.0
        # 3850 - 3863
        idx3850 = np.array(np.nonzero((wvin >= 3850) & 
                                      (wvin <= 3863))).reshape(-1).tolist()
        if idx3850:
            wv3850  = wvin[int(np.floor(np.mean(idx3850)))]
            fx3850  = np.median(fxin[idx3850])
        else:
            wv3850 = 0.0
            fx3850 = 0.0
        # 3875 - 3880
        idx3875 = np.array(np.nonzero((wvin >= 3875) & 
                                      (wvin <= 3880))).reshape(-1).tolist()
        if idx3875:
            wv3875  = wvin[int(np.floor(np.mean(idx3875)))]
            fx3875  = np.median(fxin[idx3875])
        else:
            wv3875 = 0.0
            fx3875 = 0.0
        # 3911 - 3921
        idx3911 = np.array(np.nonzero((wvin >= 3911) & 
                                      (wvin <= 3921))).reshape(-1).tolist()
        if idx3911:
            wv3911  = wvin[int(np.floor(np.mean(idx3911)))]
            fx3911  = np.median(fxin[idx3911])
        else:
            wv3911 = 0.0
            fx3911 = 0.0
        # 3938 - 3947
        idx3938 = np.array(np.nonzero((wvin >= 3938) & 
                                      (wvin <= 3947))).reshape(-1).tolist()
        if idx3938:
            wv3938  = wvin[int(np.floor(np.mean(idx3938)))]
            fx3938  = np.median(fxin[idx3938])
        else:
            wv3938 = 0.0
            fx3938 = 0.0
        # 3985 - 4000
        idx3985 = np.array(np.nonzero((wvin >= 3985) & 
                                      (wvin <= 4000))).reshape(-1).tolist()
        if idx3985:
            wv3985  = wvin[int(np.floor(np.mean(idx3985)))]
            fx3985  = np.median(fxin[idx3985])
        else:
            wv3985 = 0.0
            fx3985 = 0.0
        # 4033 - 4063
        idx4033 = np.array(np.nonzero((wvin >= 4033) & 
                                      (wvin <= 4063))).reshape(-1).tolist()
        if idx4033:
            wv4033  = wvin[int(np.floor(np.mean(idx4033)))]
            fx4033  = np.median(fxin[idx4033])
        else:
            wv4033 = 0.0
            fx4033 = 0.0
        # 4080 - 4085
        idx4080 = np.array(np.nonzero((wvin >= 4080) & 
                                      (wvin <= 4085))).reshape(-1).tolist()
        if idx4080:
            wv4080  = wvin[int(np.floor(np.mean(idx4080)))]
            fx4080  = np.median(fxin[idx4080])
        else:
            wv4080 = 0.0
            fx4080 = 0.0
        # 4153 - 4310
        idx4153 = np.array(np.nonzero((wvin >= 4153) & 
                                      (wvin <= 4310))).reshape(-1).tolist()
        if idx4153:
            wv4153  = wvin[int(np.floor(np.mean(idx4153)))]
            fx4153  = np.median(fxin[idx4153])
        else:
            wv4153 = 0.0
            fx4153 = 0.0
        # 4355 - 4357
        idx4355 = np.array(np.nonzero((wvin >= 4355) & 
                                      (wvin <= 4357))).reshape(-1).tolist()
        if idx4355:
            wv4355  = wvin[int(np.floor(np.mean(idx4355)))]
            fx4355  = np.median(fxin[idx4355])
        else:
            wv4355 = 0.0
            fx4355 = 0.0
        # 4441 - 4456
        idx4441 = np.array(np.nonzero((wvin >= 4441) & 
                                      (wvin <= 4456))).reshape(-1).tolist()
        if idx4441:
            wv4441  = wvin[int(np.floor(np.mean(idx4441)))]
            fx4441  = np.median(fxin[idx4441])
        else:
            wv4441 = 0.0
            fx4441 = 0.0
        # 4495 - 4700
        idx4495 = np.array(np.nonzero((wvin >= 4495) & 
                                      (wvin <= 4700))).reshape(-1).tolist()
        if idx4495:
            wv4495  = wvin[int(np.floor(np.mean(idx4495)))]
            fx4495  = np.median(fxin[idx4495])
        else:
            wv4495 = 0.0
            fx4495 = 0.0
        # 4720 - 4825
        idx4720 = np.array(np.nonzero((wvin >= 4720) & 
                                      (wvin <= 4825))).reshape(-1).tolist()
        if idx4720:
            wv4720  = wvin[int(np.floor(np.mean(idx4720)))]
            fx4720  = np.median(fxin[idx4720])
        else:
            wv4720 = 0.0
            fx4720 = 0.0
        # 4882 - 4914
        idx4882 = np.array(np.nonzero((wvin >= 4882) &
                                      (wvin <= 4914))).reshape(-1).tolist()
        if idx4882:
            wv4882  = wvin[int(np.floor(np.mean(idx4882)))]
            fx4882  = np.median(fxin[idx4882])
        else:
            wv4882 = 0.0
            fx4882 = 0.0
        # 4937 - 5010
        idx4937 = np.array(np.nonzero((wvin >= 4937) &
                                      (wvin <= 5010))).reshape(-1).tolist()
        if idx4937:
            wv4937  = wvin[int(np.floor(np.mean(idx4937)))]
            fx4937  = np.median(fxin[idx4937])
        else:
            wv4937 = 0.0
            fx4937 = 0.0
        # 5115 - 5865
        idx5115 = np.array(np.nonzero((wvin >= 5115) &
                                      (wvin <= 5865))).reshape(-1).tolist()
        if idx5115:
            wv5115  = wvin[int(np.floor(np.mean(idx5115)))]
            fx5115  = np.median(fxin[idx5115])
        else:
            wv5115 = 0.0
            fx5115 = 0.0
        # 5995 - 6070
        idx5995 = np.array(np.nonzero((wvin >= 5995) &
                                      (wvin <= 6070))).reshape(-1).tolist()
        if idx5995:
            wv5995  = wvin[int(np.floor(np.mean(idx5995)))]
            fx5995  = np.median(fxin[idx5995])
        else:
            wv5995 = 0.0
            fx5995 = 0.0
        # 6000 - 6400
        idx6000 = np.array(np.nonzero((wvin >= 6000) &
                                      (wvin <= 6400))).reshape(-1).tolist()
        if idx6000:
            wv6000  = wvin[int(np.floor(np.mean(idx6000)))]
            fx6000  = np.median(fxin[idx6000])
        else:
            wv6000 = 0.0
            fx6000 = 0.0
        # 6600 - 7200
        idx6600 = np.array(np.nonzero((wvin >= 6600) &
                                      (wvin <= 7200))).reshape(-1).tolist()
        if idx6600:
            wv6600  = wvin[int(np.floor(np.mean(idx6600)))]
            fx6600  = np.median(fxin[idx6600])
        else:
            wv6600 = 0.0
            fx6600 = 0.0
        # The final continuum index
        idxall = sorted(np.concatenate((idx3806,idx3850,idx3875,idx3911,idx3938,
                                        idx3985,idx4033,idx4080,idx4153,idx4355,
                                        idx4441,idx4495,idx4720,idx4882,idx4937,
                                        idx5115,idx5995,idx6000,idx6600)))
        # The returned, continuum-only arrays
        wtest    = np.array((wv6600,wv6000,wv5995,wv5115,wv4937,wv4882,
                             wv4720,wv4495,wv4441,wv4355,wv4153,wv4080,
                             wv4033,wv3985,wv3938,wv3911,wv3875,wv3850,
                             wv3806))
        idx=np.nonzero(wtest)[0].reshape(-1).tolist()
        wvout = wtest[idx]
        sptest   = np.array((fx6600,fx6000,fx5995,fx5115,fx4937,fx4882,
                             fx4720,fx4495,fx4441,fx4355,fx4153,fx4080,
                             fx4033,fx3985,fx3938,fx3911,fx3875,fx3850,
                             fx3806))
        idx = np.nonzero(sptest)[0].reshape(-1).tolist()
        specout = sptest[idx]
        #wvout   = wvin[idxall]
        #specout = specin[idxall,2,self.currspec]
    
        return wvout,specout

    # Function quad: y = a0 + a1*x + a2*x^2, called by __init__
    def quad(self,x, a0, a1, a2):
        return a0 + a1*x + a2*x**2

    # Function cubic: y = a0+ a1*x + a2*x^2 + a3*x^3, called by __init__
    def cubic(self,x, a0, a1, a2, a3):
        return a0 + a1*x + a2*x**2 + a3*x**3

    # Function quartic: used in continuum rectification
    def quartic(self,x, a):
        return a[4] + a[3]*x + a[2]*x**2 + a[1]*x**3 + a[0]*x**4

    # Function quintic: used in continuum rectification
    def quintic(self,x, a):
        return a[5] + a[4]*x + a[3]*x**2 + a[2]*x**3 + a[1]*x**4 + a[0]*x**5

    # Function sextic: used in continuum rectification
    def sextic(self,x, a):
        return a[6] + a[5]*x + a[4]*x**2 + a[3]*x**3 + a[2]*x**4 + a[1]*x**5 + \
            a[0]*x**6

    # Function septic: used in continuum rectification
    def septic(self,x, a):
        return a[7] + a[6]*x + a[5]*x**2 + a[4]*x**3 + a[3]*x**4 + a[2]*x**5 + \
            a[1]*x**6 + a[0]*x**7

    # Function octic: used in continuum rectification
    def octic(self,x, a):
        return a[8] + a[7]*x + a[6]*x**2 + a[5]*x**3 + a[4]*x**4 + a[3]*x**5 + \
            a[2]*x**6 + a[1]*x**7 + a[0]*x**8

    # Function nonic: used in continuum rectification
    def nonic(self,x, a):
        return a[9] + a[8]*x + a[7]*x**2 + a[6]*x**3 + a[5]*x**4 + a[4]*x**5 + \
            a[3]*x**6 + a[2]*x**7 + a[1]*x**8 + a[0]*x**9

    # Function decic: used in continuum rectification
    def decic(self,x, a):
        return a[10] + a[9]*x + a[8]*x**2 + a[7]*x**3 + a[6]*x**4 + a[5]*x**5 + \
            a[4]*x**6 + a[3]*x**7 + a[2]*x**8 + a[1]*x**9 + a[0]*x**10
