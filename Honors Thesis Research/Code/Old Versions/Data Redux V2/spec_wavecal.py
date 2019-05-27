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
#  RBF, 10 Jun 2018: Displayed plot in new GUI. More user friendly and allows the user to 
#		     do multiple wave calibrations at once.
#  RBF, 7 Jun 2018: Testing class wavecal_gui created to build the display without having
#		    run the entire program every time. Written using Tkinter
#  RBF, 10 Jun 2018: Plot displayed in the specframe. 
#		     Sourced from https://gist.github.com/chappers/bd910bfb0ed73c509802
#  RBF, 12 Jun 2018: Toolbar added
#  RBF, 19 Jun 2018: Merged testing class wavecal_gui with spec_wavecal




import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import sys
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkinter as tk
from matplotlib.backend_bases import key_press_handler
import copy
import math
import spectrum

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
	def __init__(self, spex, wvs, srcnames, window = 1.0):
		
		self.spectra = []   #list of Spectrum objects
		count = 0
		while count < len(srcnames):
			self.spectra.append(spectrum.Spectrum(spex[:, 4, count], srcnames[count]))
			count +=1 

		winHeight = 650             
		newfont = ("Helvetica, 20")

		self.root = tk.Tk()
		self.root.title("Wavelength Calibration")

		infoWidth = 250
		infoframe = tk.Frame(self.root, width = infoWidth, height = winHeight)
		

		instframe = tk.Frame(infoframe, width = infoWidth)
		
		instructions = "  Instructions:\t\t\t \n \t(1) Define data points \n \t(2) <Enter>: solve \n \t(3) <Ctrl-W>: close/save"	
		instlabel = tk.Label(instframe, text = instructions, justify= tk.LEFT, font= newfont)
		instlabel.pack(pady= 10)

		shortcuts   =  	"Shortcuts: \n \tRight-click to remove points \n \t<R> to reset \n \t<O> to toggle zoom \n \t<H> to toggle home"
		shortlabel = tk.Label(instframe, text = shortcuts, justify = tk.LEFT, font = newfont)
		shortlabel.pack(pady = 10)

		instframe.pack()

		buttframe = tk.Frame(infoframe, width = infoWidth, height = 100)
		
		solvebutt = tk.Button(buttframe, text = "Solve", command = self.solve_button, font = newfont)
		solvebutt.pack(side= tk.LEFT, padx = 10)
		resetbutt = tk.Button(buttframe, text = "Reset", command = self.reset_button, font = newfont)
		resetbutt.pack(side = tk.LEFT, padx = 10) 

		buttframe.pack(pady = 20)

		dataframe = tk.Frame(infoframe, width = infoWidth, height = 100)
		dataWidth = infoWidth
		
		alabel = tk.Label(dataframe, text = "a", font = newfont).grid(row = 0, column = 0)
		blabel = tk.Label(dataframe, text = "b", font = newfont).grid(row = 1, column = 0)
		clabel = tk.Label(dataframe, text = "c", font = newfont).grid(row = 2, column = 0)
		
		self.atext = tk.Entry(dataframe, font = newfont)
		self.atext.grid(row = 0, column = 1)
		self.btext = tk.Entry(dataframe, font = newfont)
		self.btext.grid(row = 1, column = 1)
		self.ctext = tk.Entry(dataframe, font = newfont)
		self.ctext.grid(row = 2, column = 1)

		dataframe.pack()

		listframe = tk.Frame(infoframe, width = infoWidth, height = 100)

		scroller = tk.Scrollbar(listframe)		

		self.imglist = tk.Listbox(listframe, font = newfont, width = 30)
		self.imglist.pack(side = tk.LEFT, pady = 10)

		scroller.configure(command = self.imglist.yview)
		scroller.pack(side = tk.LEFT,fill = 'y')
		
		for name in srcnames: self.imglist.insert(tk.END, name)
		self.imglist.selection_set(0)
		self.imglist.bind('<<ListboxSelect>>', self.on_select)
		
		finbutt = tk.Button(infoframe, text = "Finish", command = self.fin_button, font = newfont)
		finbutt.pack(side = tk.BOTTOM, pady = 10)

		listframe.pack(pady = 10)

		infoframe.grid(column = 1, row = 0)

		specwidth = 1000

		specframe = tk.Frame(self.root, height = winHeight, width = specwidth, bd = 1, relief = tk.SUNKEN) 
	
		
		#Create the figure we desire to add to an existing canvas

		numsp = spex.shape[2]
		numel = spex.shape[0]
		self.spex = spex
		self.wvs  = wvs
		self.pix  = range(numel)
		self.warr = np.zeros((numel,numsp)).copy()    #wavelengths for each spectra that are created by the curve fit
		if len(wvs) >= 4:
			self.fitparams = np.zeros((3,numsp)).copy()
		else:
			self.fitparams = np.zeros((2,numsp)).copy()

		self.currspec = 0

		fig = plt.figure(figsize = (22,15))
		self.ax = fig.gca()
       	
		self.winwidth = window/2.0  # the width of the median window taken at each point

		self.canv = FigureCanvasTkAgg(fig, master=specframe)
		self.canv.get_tk_widget().pack(side=tk.TOP, fill = 'both', expand =1)

		self.draw_graph()
		
		toolframe = tk.Frame(specframe)	
		self.toolbar = NavigationToolbar2TkAgg(self.canv, toolframe)
		
		toolframe.pack(side= tk.BOTTOM)
		specframe.grid(column = 0, row = 0)

		# Connect the different functions to the different events
		self.canv.mpl_connect('key_press_event', self.ontype)
		self.canv.mpl_connect('button_press_event', self.onclick)
		self.canv.mpl_connect('pick_event', self.onpick)		

		self.root.mainloop()
		plt.close()

	def solve_button(self):
		self.imglist.itemconfig(self.currspec, {'fg': 'green'})
		self.spectra[self.currspec].isSolved = True

		wv_pnt_coord = []
		for artist in self.ax.get_children():
			if hasattr(artist,'get_label') and artist.get_label()=='wv_pnt':
				wv_pnt_coord.append(artist.get_data())
			#elif hasattr(artist,'get_label') and artist.get_label()=='wavelengths':
			#	artist.remove()
		wv_pnt_coord = np.array(wv_pnt_coord)[...,0]
		sort_array = np.argsort(wv_pnt_coord[:,0])
		x,y = wv_pnt_coord[sort_array].T
		# Choose linear or quadratic fit to wavelengths
		if len(self.wvs) >= 4:
			params = curve_fit(self.quad,x,self.wvs,p0=[0.0,0.0,0.0])
			self.fitparams[0,self.currspec] = params[0][0]
			self.fitparams[1,self.currspec] = params[0][1]
			self.fitparams[2,self.currspec] = params[0][2]
			self.spectra[self.currspec].values = [params[0][0], params[0][1], params[0][2]]
		else:
			params = curve_fit(self.line,x,self.wvs,p0=[0.0,0.0])
			self.fitparams[0,self.currspec] = params[0][0]
			self.fitparams[1,self.currspec] = params[0][1]
			self.spectra[self.currspec].values = [params[0][0], params[0][1]]

		self.update_data()
			
		for j in self.pix:
			if len(self.wvs) >= 4:
				self.warr[j,self.currspec] = self.quad(j,params[0][0],params[0][1],params[0][2])
			else:
				self.warr[j,self.currspec] = self.line(self.pix[j],params[0][0],params[0][1])
				

	def reset_button(self):
		self.draw_graph()

	def fin_button(self):
		self.root.destroy()	

	'''
	When a new selection is made, the plot updates to show the graph that corresponds with that name.
	'''
	def on_select(self, event):
		self.currspec = event.widget.curselection()[0]
		self.draw_graph()
		
    	# ONCLICK:
    	#  When the plot is left-clicked, the nearest x-coordinate point is found.
    	#  The 'feel-radius' (picker) set to 5 points so that the spectrum points
    	#   feel it when they are clicked.
	def onclick(self, event):
		if self.toolbar.mode=='' and event.button==1:
			self.create_box(event.xdata)
		self.canv.draw()

	def create_box(self, x):
		y = self.spex[int(np.rint(x)),4,self.currspec]
		self.ax.plot(np.rint(x),y,'rs',ms=10,picker=5,label='wv_pnt')
		
    	# ONPICK:
    	#  When the user right-clicks on a chosen point, remove it
	def onpick(self, event):
		if event.mouseevent.button==3:
			if hasattr(event.artist,'get_label') and event.artist.get_label()=='wv_pnt':
				event.artist.remove()
		self.canv.draw()
		print(self.spectra[self.currspec].waves[int(np.rint(event.artist.xdata))])

    	# ONTYPE:
    	#  Type <ENTER>: Performs the wavelength calibration and prints the 
    	#   slope and y-intercept to the terminal
    	#  Type 'R': Re-set the selected points and begin wavelength calibration
    	#   over again
	def ontype(self, event):
		key_press_handler(event, self.canv, self.toolbar)
		if event.key=='enter':
			self.solve_button()
			
		# when the user hits 'r': clear the axes and plot the original spectrum
		elif event.key=='r':
			self.reset_button()
		elif event.key =='up':	
			self.update_data("up")
		elif event.key =='down':
			self.update_data("down")					
				
        
	def update_data(self, direction = None):
		self.atext.delete(0, tk.END)
		self.btext.delete(0, tk.END)
		self.ctext.delete(0,tk.END)
		
		if direction == None:
			self.atext.insert(tk.END, self.spectra[self.currspec].values[0])
			self.btext.insert(tk.END, self.spectra[self.currspec].values[1])
			self.ctext.insert(tk.END, self.spectra[self.currspec].values[2])
		
		else:
			if direction == "up":
				if self.currspec == 0:
					self.currspec = len(self.spectra) - 1
				else:
					self.currspec = self.currspec-1
			elif direction == "down":
				if self.currspec == len(self.spectra) - 1:
					self.currspec = 0
				else: 
					self.currspec = self.currspec+1
				
			self.atext.insert(tk.END, self.spectra[self.currspec].values[0])
			self.btext.insert(tk.END, self.spectra[self.currspec].values[1])
			self.ctext.insert(tk.END, self.spectra[self.currspec].values[2])

			self.imglist.select_clear(0, tk.END)
			self.imglist.select_set(self.currspec)
			self.imglist.see(self.currspec)
		
		self.draw_graph()
		

	def draw_graph(self):
		self.ax.clear()
		self.ax.plot(self.spectra[self.currspec].waves,'k-',label='spectrum')
		plt.title('Wavelength Calibration: Spectrum for: '+str(self.spectra[self.currspec].name))
		
		self.spex[:,0,self.currspec] = self.warr[:,self.currspec]

		for point in self.spectra[self.currspec].peaks:
			self.create_box(point)

		self.canv.draw()

    	# Function line: y = mx + b, called by ONTYPE
	def line(self,x, m, b):
		return m*x + b

    	# Function quad: y = ax^2 + bx + c, called by ONTPYE
	def quad(self,x,a,b,c):
		return a*x**2 + b*x + c
		


	

