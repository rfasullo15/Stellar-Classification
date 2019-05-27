'''

    7/11/2018: Class created. The mainGUI class will generate a window which asks the user what step of the data
    reduction process they would like to go to. Kind of the command central of the whole program.
    9/18/2018: Local Continuum button added so that the continuum is rectified when it is pressed.

'''
import Tkinter as tk
import generator
import s_type
import sys

class mainGUI:

    def __init__(self):

        
        
        winHeight = 600
        winWidth = 1000
        
        self.root = tk.Tk()
        self.root.title("Giraffe Butts")
        #self.root.geometry(str(winWidth) + "x" + str(winHeight))
        self.root.geometry("2150x1240")

        self.menubar = tk.Menu (self.root)

        '''
        Obligatory file menu configuration
        '''
        fileMenu = tk.Menu(self.menubar, tearoff = False)
        fileMenu.add_command(label = "Save and Quit", command = self.saveexit_button)
        fileMenu.add_command(label = "Quit", command = self.exit_button)
        
        self.menubar.add_cascade(label = "File", menu = fileMenu)
        
        '''
        Local continuum menu configuration
        '''
        contMenu = tk.Menu(self.menubar, tearoff = False)
        contMenu.add_command(label = "Generate Local Continuum", command = self.rect_button)
        contMenu.add_command(label = "Unrectify", command = self.unrect_button)
        
        self.menubar.add_cascade(label = "Local Continuum", menu = contMenu)

        '''
        Hydrogen line menu configuration
        '''

        hydroMenu = tk.Menu(self.menubar, tearoff = False)
        hydroMenu.add_command(label = "Show Hydrogen Lines", command = self.hydro_button)
        hydroMenu.add_command(label = "Show Piecwise Lines", command = self.piecewise_button)

        self.menubar.add_cascade(label = "Hydrogen Lines", menu = hydroMenu)

        '''
        Lorentz fit menu configuration
        '''
        lorMenu = tk.Menu(self.menubar, tearoff = False)
        lorMenu.add_command(label = "Create Classification Table", command = self.classtable)
        lorMenu.add_command(label = "Select Data", command = self.data_select)
        lorMenu.add_command(label = "Classify Spectra", command = self.classify)

        self.menubar.add_cascade(label = "Classification Options", menu =lorMenu)

        genMenu = tk.Menu(self.menubar, tearoff = False)
        genMenu.add_command(label = "Generate New Spectrum", command = self.generation)
        #genMenu.entryconfig("Generate New Spectrum", state = "disabled")

        #self.g = None
        self.g = generator.generator(self)
        self.g.grid(column = 0, row = 0)
        #self.g.grid_remove()

        self.menubar.add_cascade(label = "Generate", menu = genMenu)
        

        
        self.root.config(menu=self.menubar)

        self.ty = None
        #self.ty = s_type.classification(self)
        #self.ty.grid(column = 0, row = 0)
        #self.ty.grid_remove()

        #self.root.destroy()

        
        self.root.mainloop()
        

           
    def rect_button(self):
        self.ty.rectify()

    def unrect_button(self):
        self.ty.unrectify()
        
    def hydro_button(self):
        self.ty.showHydro()

    def piecewise_button(self):
        self.ty.piecewiseHydro()

    def classtable(self):
        self.ty.gen_ClassifyTable()

    def classify(self):
        self.ty.classify()

    def generation(self):
        #self.g.loadInSpectra()
        self.g.create_new()

    def data_select(self):
        self.ty.dataSelection()
    
    def saveexit_button(self):
        print("SAVE AND EXIT")

    def exit_button(self):
        sys.exit()

   

              
