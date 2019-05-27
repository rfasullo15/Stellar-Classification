'''

    7/11/2018: Class created. The mainGUI class will generate a window which asks the user what step of the data
    reduction process they would like to go to. Kind of the command central of the whole program.

'''
import Tkinter as tk
#import w_file_select as wfs
#import r_file_select as rfs
#import s_file_select as sfs
#import wavecal
#import contrect
import s_type 
import spexredux
import sys

class mainGUI:

    def __init__(self):

        
        
        winHeight = 600
        winWidth = 1000
        
        self.root = tk.Tk()
        self.root.title("Giraffe Butts")
        #self.root.geometry(str(winWidth) + "x" + str(winHeight))
        self.root.geometry("2150x1240")

        menubar = tk.Menu (self.root)

        
        fileMenu = tk.Menu(menubar, tearoff = False)
        fileMenu.add_command(label = "Save and Quit", command = self.saveexit_button)
        fileMenu.add_command(label = "Quit", command = self.exit_button)

        waveMenu = tk.Menu(menubar, tearoff = False)
        waveMenu.add_command(label = "Start", command = self.wave_button)

        conMenu = tk.Menu(menubar, tearoff = False)
        conMenu.add_command(label = "Start", command = self.rect_button)

        specMenu = tk.Menu(menubar, tearoff = False)
        specMenu.add_command(label = "Start", command = self.spec_button)
        
        menubar.add_cascade(label = "File", menu = fileMenu)
        menubar.add_cascade(label = "Wavelength Calibration", menu = waveMenu)
        menubar.add_cascade(label = "Continuum Rectification", menu = conMenu)
        menubar.add_cascade(label = "Spectral Typing", menu = specMenu)

        self.root.config(menu=menubar)

        #self.wav = wavecal.wavecal(self)
        #self.wav.grid(column = 0, row = 0)
        #self.wav.grid_remove()

        #self.con = contrect.rect(self)
        #self.con.grid(column = 0, row = 0)
        #self.con.grid_remove()

        self.ty = s_type.classification(self)
        self.ty.grid(column = 0, row = 0)
        #self.ty.grid_remove()
        
        

        self.root.mainloop()

        
        
    def wave_button(self):
        w = wfs.wfiles(self)
           
    def rect_button(self):
        r = rfs.rfiles(self)

    def spec_button(self):
        s = sfs.sfiles(self)

    def saveexit_button(self):
        print("SAVE AND EXIT")

    def exit_button(self):
        sys.exit()

    '''
    data contains (in order): Names path file, Image path file, Flat path file, Dark path file, bias path file, lamp path file, [Waves], Save path
    '''
    def setDataWave(self, data):
        self.spex = spexredux.extract(data[0], data[1], data[2], data[3], data[4], wvfiles = data[5])
        self.wav.fill(self.spex, data[6])
        self.wav.grid()
        self.root.update()

    def setDataRect(self, data):
        print("Something")

    '''
    data conatins (in order): spectra path files, save path
    '''
    def setSpectra(self, data, source):
        self.spex = spexredux.genSpec(data[0])

        if type(source) is  rfs.rfiles:
            print("CONTINUUM")
        else:
            print("SPECTRAL")

              
