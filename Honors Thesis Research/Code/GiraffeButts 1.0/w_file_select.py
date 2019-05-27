'''

7/11/2018: Class created: Generates a file explorer to select the data files you want to use in wavecalibration.

'''
import Tkinter as tk
import tkFileDialog as filedialog #tkFileDialog

class wfiles:

    def __init__(self, parent):
        self.parent = parent
        winHeight = 600
        winWidth = 800
        entryWidth = 35

        wvs = [4861.,4341.,4102.,3970.,3889., 3835.]

        self.root = tk.Toplevel(self.parent.root)
        self.root.title("File Selection for Wavelength Calibration")
        
        
        fileframe = tk.Frame(self.root, width = winWidth)

        imglabel = tk.Label(fileframe, text = "Images")
        imglabel.grid(column= 0 , row = 0)
        self.imgentry = tk.Entry(fileframe, width = entryWidth)
        self.imgentry.grid(column = 1, row = 0)
        imgbutt = tk.Button(fileframe, text = "Browse...", command = self.image_browse)
        imgbutt.grid(column = 2, row = 0, padx = 20, pady = (0, 5))

        flatlabel = tk.Label(fileframe, text = "Flats")
        flatlabel.grid(column = 3, row = 0)
        self.flatentry = tk.Entry(fileframe, width = entryWidth)
        self.flatentry.grid(column = 4, row = 0)
        flatbutt = tk.Button(fileframe, text = "Browse...", command = self.flat_browse)
        flatbutt.grid(column = 5, row = 0)

        darklabel = tk.Label(fileframe, text = "Darks")
        darklabel.grid(column= 0 , row = 1)
        self.darkentry = tk.Entry(fileframe, width = entryWidth)
        self.darkentry.grid(column = 1, row = 1)
        darkbutt = tk.Button(fileframe, text = "Browse...", command = self.dark_browse)
        darkbutt.grid(column = 2, row = 1, padx = 20, pady = (0,5))

        biaslabel = tk.Label(fileframe, text = "Bias")
        biaslabel.grid(column = 3, row = 1)
        self.biasentry = tk.Entry(fileframe, width = entryWidth)
        self.biasentry.grid(column = 4, row = 1)
        biasbutt = tk.Button(fileframe, text = "Browse...", command = self.bias_browse)
        biasbutt.grid(column = 5, row = 1)

        lamplabel = tk.Label(fileframe, text = "Lamps")
        lamplabel.grid(column= 0 , row = 2)
        self.lampentry = tk.Entry(fileframe, width = entryWidth)
        self.lampentry.grid(column = 1, row = 2)
        lampbutt = tk.Button(fileframe, text = "Browse...", command = self.lamp_browse)
        lampbutt.grid(column = 2, row = 2)

        namelabel = tk.Label(fileframe, text = "Names")
        namelabel.grid(column = 3, row = 2)
        self.nameentry = tk.Entry(fileframe, width = entryWidth)
        self.nameentry.grid(column = 4, row = 2)
        namebutt = tk.Button(fileframe, text = "Browse...", command = self.name_browse)
        namebutt.grid(column = 5, row = 2)

        fileframe.grid(column = 0, row = 0, pady = 10, padx = 10)

        self.waveframe = tk.Frame(self.root, width = winWidth)

        wavelabel = tk.Label(self.waveframe, text = "Waves:")
        wavelabel.grid(column = 0, row =  0)

        wavewidth = 10

        self.entrys = [[0,0,0,0,0,0],[0,0,0,0,0,0]]

        for val in range(len(wvs)):
            temp = tk.Entry(self.waveframe, width = 10)
            temp.insert(0, wvs[val])
            temp.grid(column = val + 1, row = 0, padx = 5)
            self.entrys[0][val] = temp

        self.waveframe.grid(column = 0, row = 1, pady = (0, 5))

        addframe = tk.Frame(self.root, width = winWidth)

        addbutt = tk.Button(addframe, text = "+ add", command = self.add_button)
        addbutt.grid(column = 0, row = 0, padx = (100, 10))

        subbutt = tk.Button(addframe, text = "- remove", command = self.remove_button)
        subbutt. grid(column = 1, row = 0, padx = (10, 100))

        addframe.grid(column = 0 , row = 2, pady = (0, 10))

        saveframe = tk.Frame(self.root, width = winWidth)

        savelabel = tk.Label(saveframe, text = "Save Path:")
        savelabel.grid(column = 0, row = 0)
        self.saveentry = tk.Entry(saveframe, width = 80)
        self.saveentry.grid(column = 1, row = 0)
        savebutt = tk.Button(saveframe, text = "Browse...", command  = self.save_browse)
        savebutt.grid(column = 2, row = 0)

        saveframe.grid(column = 0, row = 3, padx = 10)

        beginbutt = tk.Button(self.root, text = "Done", command = self.start_button)
        beginbutt.grid(column = 0, row = 4, padx = 150, pady = 10)
        
        self.root.mainloop()


    def browser(self, name, entry):
        entry.delete(0, tk.END)
        filenames = filedialog.askopenfilenames(parent = self.root, title = name)
        return filenames

    def foldbrowse(self, name, entry):
        entry.delete(0, tk.END)
        foldername = filedialog.askdirectory(parent = self.root, title = name)
        return foldername

    def image_browse(self):
        self.imgentry.insert(0, self.browser("Select Science Images", self.imgentry))

    def flat_browse(self):
        self.flatentry.insert(0, self.browser("Select Flat Images", self.flatentry))

    def dark_browse(self):
        self.darkentry.insert(0, self.browser("Select Dark Images", self.darkentry))

    def bias_browse(self):
        self.biasentry.insert(0, self.browser("Select Bias Images", self.biasentry))

    def lamp_browse(self):
        self.lampentry.insert(0, self.browser("Select Lamp Images", self.lampentry))

    def name_browse(self):
        self.nameentry.insert(0, self.browser("Select Name File", self.nameentry))

    def save_browse(self):
        self.saveentry.insert(0, self.foldbrowse("Select Save Path", self.saveentry))

    def add_button(self):
        temp = tk.Entry(self.waveframe, width = 10)
        
        if self.entrys[0][5] == 0:
            index = len(self.entrys[0]) - self.entrys[0].count(0)
            temp.grid(column= 1+index, row = 0, padx = 5)
            self.entrys[0][index] = temp
        else:
            index = len(self.entrys[1]) - self.entrys[1].count(0)
            temp.grid(column = 1 + index, row = 1, padx = 5)
            self.entrys[1][index] = temp
            
        self.root.update()
        

    def remove_button(self):
        if self.entrys[1][5] != 0: #The last element of the last list
            self.entrys[1][5].grid_remove()
            self.entrys[1][5] = 0
        elif self.entrys[1][0] ==0 and self.entrys[0][5] != 0: #last element of the first list
            self.entrys[0][5].grid_remove()
            self.entrys[0][5] = 0
        else:
            row = 0
            while row < 2:
                column = 0
                while column < len(self.entrys[row]) - 1:
                    if self.entrys[row][column] != 0 and self.entrys[row][column + 1] == 0:
                        self.entrys[row][column].grid_remove()
                        self.entrys[row][column] = 0
                    column +=1
                row+=1
                
        self.root.update()

   

    def parse_paths(self, filestring):
        if filestring[0] == "{":
            filestring = filestring.replace("{", '').replace("}", '')
            
        if type(filestring) is str:
            d = ".fit "
            paths = [(e+d).strip(" ") for e in filestring.split(d)]
            paths[len(paths) - 1] = paths[len(paths) -1][:-4]

            return paths
        else:
            return filestring

    '''
    returns in this order: Names, Images, Flats, Darks, Bias, Lamps, [Waves], Save Path
    '''
    def start_button(self):
        waves = []
        for lst in self.entrys:
            for widgy in lst:
                if type(widgy) is not int:
                    waves.append(widgy.get())
        #This may cause problems when you transition to linux
        self.parent.setDataWave([self.parse_paths(self.nameentry.get()), self.parse_paths(self.imgentry.get()), self.parse_paths(self.flatentry.get()), self.parse_paths(self.darkentry.get()), self.parse_paths(self.biasentry.get()), self.parse_paths(self.lampentry.get()), waves, self.saveentry.get()])
        self.root.destroy()
        


        

        
    
