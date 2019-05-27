import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


main_path = os.path.dirname(__file__)

name_path = main_path + "\SpectralStandardsReadable.txt"
names = pd.read_csv(name_path, delim_whitespace = True)
#count = [11, 52, 70]
#names = ["HD036512_20171211.txt", "HD034759_20171211.txt", "HD071155_20180302.txt"]
num = 1
for star_name in names["FileName"]:
    data_path = "C:\Users\90rfa\Documents\Honors Thesis Data\Generator2\\ " + str(num) + "G2"
    #data_path2 = "C:\Users\90rfa\Documents\Honors Thesis Data\Generator3\\ " + str(num) + "G3" 

    index = 0
    while index<30:
        table = pd.read_csv(data_path + str(index).zfill(2) + "-" +star_name, delim_whitespace = True)
        #table2 =pd.read_csv(data_path2 + str(index).zfill(2) + "-" +star_name, delim_whitespace = True)
        #plt.subplot(211)
        plt.plot(table["wv"], table["rms"])
        #plt.subplot(212)
        #plt.plot(table2["wv"], table2["rms"])
        
        index +=1
    
    orig_path = main_path + "\Standards\\"
    original = pd.read_csv(orig_path + star_name, delim_whitespace = True)
    #plt.subplot(211)
    plt.plot(original["wv"], original["rms"], "k-")
    plt.title(star_name)

    #plt.subplot(212)
    #plt.plot(original["wv"], original["rms"], "k-")
    
    plt.show()

    num +=1
