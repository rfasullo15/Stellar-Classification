'''
This class is responsible for rendering the gui that displays the wave
calibration. 

HISTORY:

6/7/2018- File created, configuration started. The display will be built and 
	  then I will plug in the actual functionality of the wave calibration. Written
	  using Tkinter. 
	  ~GUI Complete!!~

6/10/2018- Plot displayed in the specframe. Process sourced from https://gist.github.com/chappers/bd910bfb0ed73c509802
	   with modifications to make it compatible with pylab.

6/12/2018- Toolbar added

@author rfasullo

'''
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class wavecal_gui:

	def __init__(self, spex, wvs,  wcal, srcnames, window):
		self.wcal = wcal #handle on basically the controller
		self.srcnames = srcnames

		winHeight = 650             
		newfont = ("Helvetica, 12")

		root = tk.Tk()
		root.title("Wavelength Calibration")

		infoWidth = 250
		infoframe = tk.Frame(root, width = infoWidth, height = winHeight)
		

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
		
		self.atext = tk.Entry(dataframe, font = newfont).grid(row = 0, column = 1)
		self.btext = tk.Entry(dataframe, font = newfont).grid(row = 1, column = 1)
		self.ctext = tk.Entry(dataframe, font = newfont).grid(row = 2, column = 1)

		dataframe.pack()

		listframe = tk.Frame(infoframe, width = infoWidth, height = 100)
		
		self.imglist = tk.Listbox(listframe, font = newfont, width = 30)
		self.imglist.pack(pady = 10)
		
		for name in srcnames: self.imglist.insert(tk.END, name)
		self.imglist.selection_anchor(0)
		self.imglist.bind('<<ListboxSelect>>', self.on_select)
		

		finbutt = tk.Button(listframe, text = "Finish", command = self.fin_button, font = newfont)
		finbutt.pack(pady = 10)

		listframe.pack(pady = 10)


		infoframe.grid(column = 1, row = 0)

		specwidth = 1000

		specframe = tk.Frame(root, height = winHeight, width = specwidth, bd = 1, relief = tk.SUNKEN) 
	
		
		#Create the figure we desire to add to an existing canvas

		numsp = spex.shape[2]
		numel = spex.shape[0]
		self.spex = spex
		self.wvs  = wvs
		self.pix  = range(numel)
		self.warr = np.zeros((numel,numsp)).copy()
		if len(wvs) >= 4:
			self.fitparams = np.zeros((3,numsp)).copy()
		else:
			self.fitparams = np.zeros((2,numsp)).copy()

		currspec = 0

		fig = plt.figure(figsize = (22,15))
		self.ax = fig.gca()
       	
		self.winwidth = window/2.0  # the width of the median window taken at each point
            
		self.ax.plot(self.spex[:,4,currspec],'k-',label='spectrum')
		plt.title('Wavelength Calibration: Spectrum for: '+str(srcnames[currspec]))
		
		self.spex[:,0,currspec] = self.warr[:,currspec]

		self.canv = FigureCanvasTkAgg(fig, master=specframe)
		self.canv.draw()
		self.canv.get_tk_widget().pack(side=tk.TOP, fill = 'both', expand =1)
		
		toolframe = tk.Frame(specframe)
		#locatorframe = tk.Frame(toolframe)	
		toolbar = NavigationToolbar2TkAgg(self.canv, toolframe)
		#toolbar.pack(side= tk.LEFT)
		#canv._tkcanvas.pack(side= tk.BOTTOM, fill = tk.BOTH, expand =1)

		#spacer = tk.Frame(toolframe, height = 50, width = 900)
		#spacer.pack(side = tk.RIGHT)

		#locatorframe.pack(side= tk.RIGHT)
		#toolframe.pack(side= tk.BOTTOM)
		specframe.grid(column = 0, row = 0)

		# Connect the different functions to the different events
		self.canv.mpl_connect('key_press_event', self.ontype)
		self.canv.mpl_connect('button_press_event', self.onclick)
		self.canv.mpl_connect('pick_event', self.onpick)

		
		#self.canv.force_focus()
		root.mainloop()
	#END CONSTRUCTOR

	def solve_button(self):
		print("SOLVE")
		self.imglist.itemconfig(self.imglist.curselection()[0], {'fg': 'green'})

	def reset_button(self):
		print("RESET")

	def fin_button(self):
		print("FINISH")
	
	def on_key_press(self, event):
		self.wcal.ontype(event)

	def on_click(self, event):
		self.wcal.onclick(event)

	def on_pick(self, event):
		self.wcal.onpick(event)

	'''
	When a new selection is made, the plot updates to show the graph that corresponds with that name.
	'''
	def on_select(self, event):
		currspec = event.widget.curselection()[0]
		self.ax.clear()

		self.ax.plot(self.spex[:,4,currspec],'k-',label='spectrum')
		plt.title('Wavelength Calibration: Spectrum for: '+str(self.srcnames[currspec]))
		
		#self.spex[:,0,currspec] = self.warr[:,currspec]
		
		self.canv.draw()

#END CLASS

#gui = wavecal_gui(None, None, None)