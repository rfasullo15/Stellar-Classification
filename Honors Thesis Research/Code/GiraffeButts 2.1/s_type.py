'''
8-30-2018 RBF: Created file.
9-11-2018 RBF: New Version to created. Cleaned up the code so only the essentials are included.
9-13-2018 RBF: Peak location successfully implemented.
10-16-2018 RBF: Gen Classificaiton Table method created.
10-18-2017 RBF: Classification algorithm developed using RandomForestClassifier from sklearn
10-18-2017 RBF: First fit complete with 95% Accuracy

This will create a pandas data frame that will house all of the values for the respective spectra.
'''

import pandas as pd
import numpy as np
import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import spectrum
import os.path
import math
from scipy.optimize import curve_fit
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV

from sklearn.model_selection import train_test_split


class classification(tk.Frame):

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
        
        #headers = ["H9 3835", "H8 3889", "Hep 3970", "Hdel 4101", "Hgam 4340", "Hb 4861", "H9 wing", "H8 wing", "Hdel wing", "Hgram wing", "Hb wing", "He I 4009", "He I 4026", "He I 4144", "He I 4387", "He I 4387", "He I 4471", "He I 4121", "He I 4922", \
         #                   "He I 4714", "He II 4200", "He II 4541", "Si IV 4089", "Si IV 4116", "Si II 4128", "Si II 4130", "Si II 4201", "Si II 3856", "Si II 3862", "Si II 4002", "Si II 4028", "Si II 4076", "C II 4267", "Si III 4552", "Mg II 4481", "Mg II 3984", \
         #                   "Ca II K 3984", "Mn I 4030", "Fe I 4046", "Fe I 4271", "Fe I 4383", "Ca I 4226", "Cr II 4172", "Cr II 4111", "Cr II 3866", "Sr II 4216", "Mn II 4136", "Mn II 4206", "Mn II 4252", "Mn II 4259", "Eu II 4205", "Eu 4130", "Fe II 4172", \
         #                    "Fe II 4233", "Fe II 4395", "Ti II 4179", "Ti II 4400", "N II 3995", "3905-4050", "4051-4215", "4216-4700", "4701-4950"]
        #df  = pd.DataFrame(np.zeros(62,1)) #, index = ["I am a spectrum"], columns = headers )

        #zero_dat = np.zeros(shape = (1,len(headers)))
        #df = pd.DataFrame(zero_dat, index = ["Poops"], columns = headers)

    '''
    Loads in the text files of the spectra. Currently works with the list of strongly identified spectra provided by DGW
    '''
    def loadInSpectra(self):
        self.spType = "" #Single point of maintainence!!!  C- Complete, NL - No Lumin Class, _blank_ -only letters, W- Whole Number 
        try:
            classtable_path = "C:\\Users\\90rfa\\Dropbox\\Honors Thesis Research\\Code\\GiraffeButts 2.1\\Classtable" + self.spType+ ".txt"
            self.classtable = pd.read_csv(classtable_path, delim_whitespace = True)
        except:
            '''
            read in the table containing the file names and the classifications of the file names
            '''
            list_path = "C:\\Users\\90rfa\\Dropbox\\Honors Thesis Research\\Code\\GiraffeButts 2.1\\Classifications.txt"
            pathtable = pd.read_csv(list_path, delim_whitespace = True)

            #nameFile = open(list_path, "r")
            '''
            Read in and create the spectra for the spectra table
            '''
            folder_path = "C:\\Users\\90rfa\\Documents\\data\\"
            self.spectra = []
            for name in pathtable["Name"]:
                name = name.strip()
                table = pd.read_csv(folder_path+name, delim_whitespace = True)
                self.spectra.append(spectrum.Spectrum(table, name))

            '''
            Give each spectrum a classification
            '''
            index = 0
            while index<len(self.spectra):

                if(self.spType == ""): self.spectra[index].classification = pathtable["SpTypeAlphaOnly"][index]
                elif (self.spType == "W"): self.spectra[index].classification = pathtable["SpTypeWholeNumber"][index]
                elif (self.spType == "NL"): self.spectra[index].classification = pathtable["SpTypeNoLumin"][index]
                elif (self.spType == "C"): self.spectra[index].classification = pathtable["SpTypeComplete"][index]
                else: print("ERROR")
                index +=1
                
            '''
            Populate Scroller
            '''
            for spect in self.spectra: self.imglist.insert(tk.END, spect.name)
            self.imglist.select_set(self.currspec)
            self.imglist.bind('<<ListboxSelect>>', self.on_select)

            self.draw_graph()
            
            self.gen_ClassifyTable()


        self.classify()

        

    '''
    Puts the information about the lorentz fits for each spectra into a table
    '''
    def gen_ClassifyTable(self):
        headers = ["Name", "Classification", "H8_L_Gam", "H8_L_Avg", "H8_L_Cont", "H8_L_Strength", \
                                                   "H8_R_Gam", "H8_R_Avg", "H8_R_Cont", "H8_R_Strength", \
                                                   "Hep_L_Gam", "Hep_L_Avg", "Hep_L_Cont", "Hep_L_Strength", \
                                                   "Hep_R_Gam", "Hep_R_Avg", "Hep_R_Cont", "Hep_R_Strength", \
                                                   "Hdel_L_Gam", "Hdel_L_Avg", "Hdel_L_Cont", "Hdel_L_Strength", \
                                                   "Hdel_R_Gam", "Hdel_R_Avg", "Hdel_R_Cont", "Hdel_R_Strength", \
                                                   "Hgam_L_Gam", "Hgam_L_Avg", "Hgam_L_Cont", "Hgam_L_Strength", \
                                                   "Hgam_R_Gam", "Hgam_R_Avg", "Hgam_R_Cont", "Hgam_R_Strength", \
                                                   "Hb_L_Gam", "Hb_L_Avg", "Hb_L_Cont", "Hb_L_Strength", \
                                                   "Hb_R_Gam", "Hb_R_Avg", "Hb_R_Cont", "Hb_R_Strength"]
        rows = []
        for spectrum in self.spectra:
            row =[spectrum.name, spectrum.classification]
            for line in spectrum.hydros:
                #print(line.name)
                for val in line.poptL:
                    row.append(val)
                for val in line.poptR:
                    row.append(val)
            rows.append(row)
        self.classtable = pd.DataFrame(rows, columns = headers)

        self.classtable.to_csv("Classtable" +self.spType+ ".txt", sep = '\t')
        
        
        

    def classify(self):
        class_mapping = {label:idx for idx, label in enumerate(np.unique(self.classtable["Classification"]))}
        #print(len(class_mapping))
        self.classtable["Classification"] = self.classtable["Classification"].map(class_mapping)
        feat_labels = self.classtable.columns[2:]
        

        param_grid = {
            'n_estimators' : [100, 300, 500, 700, 1000, 2000],              #number of trees in the forest
            'max_features': [5, 10, 'auto', 'sqrt', 'log2', None],               #The maximum number of features considered for splitting a node
            'max_depth' : [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],        #Max depth of the tree
            'bootstrap': [True, False],                                                 #Whether samples are being pulled with replacement
            'min_samples_leaf':[1,2,4,6],                                              #Min number of data points in a leaf node
            'min_samples_split': [2,5,10]}                                              #Min number of data points in a node before it splits into smaller nodes

        forest = RandomForestClassifier()
        rf_random = RandomizedSearchCV(estimator = forest, param_distributions = param_grid, n_iter = 100, cv = 10, verbose = 2, random_state = 100, n_jobs = -1)

        trainData, testData = train_test_split(self.classtable.values, test_size = 20)

        answers = np.asarray([spect[1] for spect in trainData])
        testanswers = np.asarray([spect[1] for spect in testData])
        trainData = [np.asarray(spect[2:], dtype = float) for spect in trainData]
        testData = [np.asarray(spect[2:], dtype = float) for spect in testData]

        rf_random.fit(trainData, answers)
        print("FIT COMPLETE")

        print(rf_random.best_estimator_)

        masterforest = rf_random.best_estimator_


        
        
        #forest = RandomForestClassifier(n_estimators=1000, random_state = 0, n_jobs = -1)      #Classifying forest
        
        kf = KFold(n_splits = 10)
        avgAcc = 0

        #print(kf)
        
        '''
        Using cross validation to assess the acccuracy of the forest
        '''
        
        for train_index, test_index in kf.split(self.classtable.values):
            
            trainData, testData= self.classtable.values[train_index], self.classtable.values[test_index]
            answers = np.asarray([spect[1] for spect in trainData])
            testanswers = np.asarray([spect[1] for spect in testData])
            trainData = [np.asarray(spect[2:], dtype = float) for spect in trainData]
            testData = [np.asarray(spect[2:], dtype = float) for spect in testData]

            #rf_random.fit(trainData, answers)
            masterforest.fit(trainData, answers)
            print("FIT COMPLETE")

            #accuracy = rf_random.score(testData, testanswers)
            accuracy = masterforest.score(testData, testanswers)

            avgAcc += accuracy 
            
        avgAcc = avgAcc/kf.get_n_splits()

        print("AVG ACCURACY")
        print(avgAcc)


        ''' HERE '''
        #print(masertforest.estimators_)

        #print(rf_random.best_estimator_)
         
            
            

        #print(kf.get_n_splits())

        
        
        
        #print(trainData)

        
        #print(testanswers )
        
        #print(testData)
        


        #fangorn.fit(trainData, answers)
        #print("FIT COMPLETE")
        
        #accuracy = fangorn.score(testData, testanswers)
        #print("ACCURACY")
        #print(accuracy)

        
        #importances = fangorn.feature_importances_

        #indeces = np.argsort(importances)[::-1]

        '''
        importArray = []
        for f in range(len(feat_labels)):
            importArray.append([feat_labels[indeces[f]], importances[indeces[f]]])

        importTable = pd.DataFrame(importArray, columns=["Feature", "Importance"])

        importTable.to_csv("ImportTable" +self.spType+ ".txt", sep = '\t')
        '''
        
            
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

    ''' 
    hydro selects the points for all of the hydrogen balmer series absorption peaks
    '''
    def hydro(self):
        for line in self.spectra[self.currspec].hydros:
            self.selectpeaks(line.index)

        
    def selectpeaks(self, index):
 
        y = self.spectra[self.currspec].df["rms"].iloc[index]                                                                            #Get the minimum of the selected rows from rms
        x = self.spectra[self.currspec].df["wv"].iloc[index]                                          #Index of the location of the minimum in rms
        self.ax.plot(x,y,'rs',ms=10,picker=5,label='wv_pnt')           # Draw the box
        
    def rectify(self):
        self.ax.clear()
        self.ax.plot(self.spectra[self.currspec].df["wv"], self.spectra[self.currspec].df["local"], "k-")
        self.canv.draw()


    def unrectify(self):
        
        self.ax.clear()
        self.ax.plot(self.spectra[self.currspec].df["wv"], self.spectra[self.currspec].df["rms"], "k-")
        self.hydro()
        self.canv.draw()

    def showHydro(self):
        plt.figure(2, figsize = (10, 6))


        c = 0
        while c < len(self.spectra[self.currspec].hydros):
            '''
            Plotting the bounds of the hydrogen lines on the main graph
            '''
            line = self.spectra[self.currspec].hydros[c]
            xR = self.spectra[self.currspec].df["wv"][line.rightIndex]
            yR = self.spectra[self.currspec].df["rms"][line.rightIndex]
            self.ax.plot(xR,yR, 'go', ms = 5, label = 'hydro_pnt')
            xL = self.spectra[self.currspec].df["wv"][line.leftIndex]
            yL = self.spectra[self.currspec].df["rms"][line.leftIndex]
            self.ax.plot(xL, yL, 'go', ms = 5, label = 'hydro_pnt')
            '''
            Making subplots for each of the individual lines
            '''
            x = line.hydrodf["wv"]
            plt.subplot(231 + c)
            plt.plot(x, line.hydrodf["local"], "k-")
            plt.title(line.name)

            '''
            Plotting the lorentz fits (if they exist)
            
            if(line.poptL[0] != 0):
                leftX = x[0:line.newCenterIdx]
                plt.plot(leftX, line.lorentzFit(leftX, line.poptL[0], line.poptL[1], line.poptL[2], line.poptL[3]))
            if(line.poptR[0] != 0):
                rightX = x[line.newCenterIdx: line.length]
                plt.plot(rightX, line.lorentzFit(rightX, line.poptR[0], line.poptR[1], line.poptR[2], line.poptR[3]))
            '''
            c+=1

        self.canv.draw()  
        plt.show()
        
        

    def piecewiseHydro(self):
        print("HIDE")
        


        







        
