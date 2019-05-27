'''
    History:

    RBF, 26 June, 2018: Created class. The spec_rec will render a gui for the spectral rectification.

'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import Tkinter as tk
from matplotlib.backend_bases import key_press_handler

class rect:

    def __init__(self, srcnames):
        winHeight = 600
        newfont = ("Helvetica, 15")

        self.root = tk.Tk()
        self.root.title("Continuum Rectification")

        infoWidth = 200
        infoframe = tk.Frame (self.root, width = infoWidth, height= winHeight)

        instructions = "Instructions: \n \t1) Define data points \n \t2) <Enter>: Solve \n \t3) <D> View rectified spectrum \n \t4) <Ctrl-W>: Close/save"
        instlabel = tk.Label(infoframe, text = instructions, justify = tk.LEFT, font = newfont)
        instlabel.grid(row= 0, column = 0, pady = 10)

        shortcuts = "Shortcuts: \n \tRight-click to remove points \n \t<R> to reset"
        shortlabel = tk.Label(infoframe, text = shortcuts, justify = tk.LEFT, font = newfont)
        shortlabel.grid(row= 1, column = 0, pady = 10)

        buttframe = tk.Frame(infoframe, width = infoWidth, height = 100)

        rectbutt = tk.Button(buttframe, text = "Rectify", command = self.rect_button, font = newfont)
        rectbutt.pack(side = tk.LEFT, padx = 10)
        resetbutt = tk.Button(buttframe, text = "Reset", command = self.reset_button, font = newfont)
        resetbutt.pack(side = tk.LEFT, padx = 10)

        buttframe.grid(row = 2, column = 0, pady = 10)

        listframe = tk.Frame(infoframe, width = infoWidth, height = 100)

        scroller = tk.Scrollbar(listframe)

        self.imglist = tk.Listbox(listframe, font = newfont, width = 30)
        self.imglist.pack(side = tk.LEFT, fill= 'y')

        scroller.configure(command = self.imglist.yview)
        scroller.pack(side = tk.LEFT, fill = 'y')
        
        for name in srcnames: self.imglist.insert(tk.END, name)
        self.imglist.selection_set(0)
        self.imglist.bind("<<ListboxSelect>>", self.on_select)

        listframe.grid(row = 3, column = 0, pady = 10)

        finbutt = tk.Button(infoframe, text = "Finish", command = self.fin_button, font = newfont)
        finbutt.grid(row = 4, column = 0, pady = 10)

        infoframe. grid(column = 1, row = 0)

        specwidth = 550

        specframe = tk.Frame(self.root, height = winHeight, width = specwidth, bd = 1, relief = tk.SUNKEN)

        #Create the figure we want on the canvas (Dummy for now)

        fig = plt.figure(figsize = (18,12))
        #self.ax = fig.gca()
        

        self.winwidth = 1/2

        self.canv = FigureCanvasTkAgg(fig, master = specframe)
        self.canv.get_tk_widget().pack(side = tk.TOP, fill = "both", expand = 1)

        self.currspec = 0

        X1 = np.linspace(0,2*np.pi, 50)
        Y1 = np.sin(X1)
        plt.subplot(211)
        plt.plot(X1,Y1)

        X2 = np.linspace(0,2*np.pi,50)
        Y2 = np.sin(X2)
        plt.subplot(212)
        plt.plot(X2,Y2)
        

        

        plt.title("Continuum Rectification: Spectrum for: " + str(srcnames[self.currspec]))

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
        print("Rectum")

    def reset_button(self):
        print("Reset")

    def fin_button(self):
        print("Finish")

    def on_select(self, event):
        print("Select")

    def ontype(self, event):
        print("Type")

    def onclick(self, event):
        print("Click")

    def onpick(self, event):
        print("Pick")
    
