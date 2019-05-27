'''

    7/11/2018: Class created. The mainGUI class will generate a window which asks the user what step of the data
    reduction process they would like to go to. Kind of the command central of the whole program.
    9/18/2018: Local Continuum button added so that the continuum is rectified when it is pressed.

'''
import Tkinter as tk
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
        Lorentz fit menu configuration
        '''
        lorMenu = tk.Menu(self.menubar, tearoff = False)
        lorMenu.add_command(label = "Example Lorentz", command = self.lorEx_button)
        lorMenu.add_command(label = "Generate All Lorentz", command = self.lor_button)

        self.menubar.add_cascade(label = "Lorentz Fit", menu = lorMenu)
        self.menubar.entryconfig("Lorentz Fit", state = tk.DISABLED)

        
        self.root.config(menu=self.menubar)

        self.ty = s_type.classification(self)
        self.ty.grid(column = 0, row = 0)
        #self.ty.grid_remove()

        self.root.mainloop()

           
    def rect_button(self):
        self.ty.localcontinuum()
        self.menubar.entryconfig("Lorentz Fit", state = tk.NORMAL)

    def unrect_button(self):
        self.ty.unrectify()
        self.menubar.entryconfig("Lorentz Fit", state = tk.DISABLED)

    def lorEx_button(self):
        self.ty.createExampleLorentz()

    def lor_button(self):
        self.ty.createAllLorentz()

    def saveexit_button(self):
        print("SAVE AND EXIT")

    def exit_button(self):
        sys.exit()

   

              
