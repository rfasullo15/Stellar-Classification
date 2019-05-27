'''
01-07-2019: Created to generate randomly perturbed data. 

This will create a pandas data frame that will house all of the values for the respective spectra.
'''

import Tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import spectrum
import random
class generator(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent.root)
        pd.set_option("display.max_rows", 200)
        pd.set_option("display.max_columns", 200)
        np.set_printoptions(threshold = 'nan')
        self.rent = parent
        self.currspec = 0

        winHeight = 600
        specwidth = 800

        specframe = tk.Frame(self, height = winHeight, width = specwidth)

        fig = plt.figure(figsize = (17, 9))
        self.ax = fig.gca()

        self.winwidth = 1/2

        self.canv = FigureCanvasTkAgg(fig, master = specframe)
        self.canv.get_tk_widget().pack(side = tk.TOP, fill = 'both', expand = 1)

        #self.setFigure()

        toolframe = tk.Frame(specframe)
        self.toolbar = NavigationToolbar2TkAgg(self.canv, toolframe)

        toolframe.pack(side = tk.BOTTOM)
        specframe.grid(column = 0, row = 0)

        infoWidth = 200
        

        infoframe = tk.Frame(self, width = infoWidth, height = winHeight)

        listframe = tk.Frame(infoframe, width = infoWidth, height = 100)

        scroller = tk.Scrollbar(listframe)        

        self.imglist = tk.Listbox(listframe, width = 30, height = 10)
        self.imglist.configure(yscrollcommand = scroller.set)
        self.imglist.pack(side = tk.LEFT, pady = 10)

        scroller.configure(command = self.imglist.yview)
        scroller.pack(side = tk.LEFT,fill = 'y')

        listframe.pack(pady = 10)
        infoframe.grid(column = 1, row = 0)

        self.loadInSpectra()

        

        plt.close()
        
    '''
    Loads in the text files of the spectra. Currently works with the list of strongly identified spectra provided by DGW
    '''
    def loadInSpectra(self):
        '''
        read in the table containing the file names and the classifications of the file names
        '''
        list_path = "C:\\Users\\90rfa\\Dropbox\\Honors Thesis Research\\Code\\GiraffeButts 2.1\\Classifications.txt"
        pathtable = pd.read_csv(list_path, delim_whitespace = True)

        #nameFile = open(list_path, "r")
        '''
        Read in and create the spectra for the spectra table
        '''
        folder_path = "C:\Users\90rfa\Documents\Honors Thesis Data\data_v2\\"
        self.spectra = []
        for name in pathtable["Name"]:
            name = name.strip()
            table = pd.read_csv(folder_path+name, delim_whitespace = True)
            self.spectra.append(spectrum.Spectrum(table, name))
            
        '''
        Populate Scroller
        
        for spect in self.spectra: self.imglist.insert(tk.END, spect.name)
        self.imglist.select_set(self.currspec)
        self.imglist.bind('<<ListboxSelect>>', self.on_select)
        '''

        #self.draw_graph()

    def draw_graph(self):

        self.ax.clear()
        self.ax.plot(self.spectra[self.currspec].df["wv"], self.spectra[self.currspec].df["rms"], 'r-', label = 'spectrum')
        #self.hydro()

        self.canv.draw()

    '''
    When a new selection is made, the plot updates to show the graph that corresponds with that namaste.
    '''
    def on_select(self, event):
        self.currspec = event.widget.curselection()[0]
        self.draw_graph()

    def create_new(self):
        count = 0
        for index in range(96):
            current = self.spectra[index]
            count +=1
            print(current.name)
            for val in range(30):
                wv = current.df["wv"]
                rms = np.random.normal(loc=current.df["rms"], scale = abs(0.01*current.df["rms"]))
                snr = current.df["snr"]

                data = {"wv": wv, "rms":rms, "snr": snr}
                
                df = pd.DataFrame(data)

                self.spectra.append(spectrum.Spectrum(df, str(count) + "G2" + str(val).zfill(2) + "-" + current.name))
                f = open("C:\Users\90rfa\Documents\Honors Thesis Data\Generator2\ " + str(count) + "G2" + str(val).zfill(2) + "-" +  current.name, "w+")
                f.write(df.to_string(index = False))
                f.close()

        for spect in self.spectra: self.imglist.insert(tk.END, spect.name)
        self.imglist.select_set(self.currspec)
        self.imglist.bind("<<ListboxSelect>>", self.on_select)

        self.draw_graph()

