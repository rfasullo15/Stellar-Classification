'''
8-30-2017 RBF: Created file.

This will created a pandas data frame that will house all of the values for the respective spectra.
'''

import pandas as pd
import numpy as np
import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import os,glob
import spectrum
import pickle
import os.path
import bisect


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
        #try:
           # f = open("C:\\Users\\90rfa\\Documents\\Dumping Grounds.txt")

            #self.spex = pickle.load(f)
        #except:
        folder_path = "C:\\Users\\90rfa\\Documents\\Testing Data\\"
        df = pd.read_csv(folder_path+"3CenA_20180607.txt", delim_whitespace = True)

        self.ax.clear()
        self.ax.plot(df["wv"], df["rms"], "k-")

        wv = np.around(np.array(df["wv"]), 0).astype(int)
        
        indeces = np.where(wv == 3835)
        x = df["wv"][indeces]
        print(x)

        #rms = np.array(df["rms"])
        #y = np.sort(rms[indeces[0])
        #print(rms[indeces[0]])

        
        #y = df["rms"]
        #y = df["rms"][x]
        #self.ax.plot(df["wv"][x],y,'rs',ms=10,picker=5,label='wv_pnt')
    
        
        
       

    '''
    def genFile(self):
        folder_path = "C:\\Users\\90rfa\\Documents\\Testing Data\\"
        spex = []
        for filename in glob.glob(os.path.join(folder_path, '*.txt')):
            with open(filename, 'r') as f:
                text = f.readline()
                name = filename[38:].strip(".txt") #30 for the real set
                print(name)
                speckles = spectrum.Spectrum(name)
                wv = []
                raw = []
                rms = []
                rectified = []
                waves = []
                snr = []
                
                for line in f:
                    stuff = line.strip("\n").split(" ")
                    wv.append(stuff[0])
                    raw.append(stuff[1])
                    rms.append(stuff[2])
                    rectified.append(stuff[3])
                    waves.append(stuff[4])
                    snr.append(stuff[5])

                speckles.setVals(wv, raw, rms, rectified, waves, snr)
                spex.append(speckles)
        dumpingGrounds = open ("C:\\Users\\90rfa\\Documents\\Dumping Grounds.txt", "w")
        pickle.dump(spex, dumpingGrounds)
        dumpingGrounds.close()
        return spex
    '''
    






   

