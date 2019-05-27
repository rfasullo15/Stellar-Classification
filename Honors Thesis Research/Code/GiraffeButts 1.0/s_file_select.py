'''

7/18/2018: Class created: Generates a file explorer to select the data files you want for spectral typing

'''
import Tkinter as tk
import tkFileDialog as filedialog

class sfiles:

    def __init__(self,parent):
        self.parent = parent

        winHeight = 600
        winWidth = 800

        self.root = tk.Toplevel(self.parent.root)
        self.root.title("File Selection for Spectral Typing")

        speclabel = tk.Label(self.root, text = "Spectra")
        speclabel.grid(column= 0 , row = 0)
        self.specentry = tk.Entry(self.root, width = 80)
        self.specentry.grid(column = 1, row = 0)
        specbutt = tk.Button(self.root, text = "Browse...", command = self.spec_browse)
        specbutt.grid(column = 2, row = 0, padx = 20, pady = (0, 5))

        savelabel = tk.Label(self.root, text = "Save Path:")
        savelabel.grid(column = 0, row = 1)
        self.saveentry = tk.Entry(self.root, width = 80)
        self.saveentry.grid(column = 1, row = 1)
        savebutt = tk.Button(self.root, text = "Browse...", command  = self.save_browse)
        savebutt.grid(column = 2, row = 1)

        beginbutt = tk.Button(self.root, text = "Done", command = self.start_button)
        beginbutt.grid(column = 1, row = 2, padx = 150, pady = 10)
        
        self.root.mainloop()

    def browser(self, name, entry):
        entry.delete(0, tk.END)
        filenames = filedialog.askopenfilenames(parent = self.root, title = name)
        return filenames

    def foldbrowse(self, name, entry):
        entry.delete(0, tk.END)
        foldername = filedialog.askdirectory(parent = self.root, title = name)
        return foldername

    def spec_browse(self):
        self.specentry.insert(0, self.browser("Select Spectra", self.specentry))

    def save_browse(self):
        self.saveentry.insert(0, self.foldbrowse("Select Save Path", self.saveentry))

    def parse_paths(self, filestring):
        if type(filestring) is str:
            filestring = filestring.strip("{").strip("}")
            paths = filestring.split("} {")

            return paths
        else:
            return filestring

    '''
    gives mainGUI (in order): Spectra paths, save path
    '''
    def start_button(self):
        
        self.parent.setSpectra([self.parse_paths(self.specentry.get()), self.parse_paths(self.saveentry.get())], self)
        self.root.destroy()
