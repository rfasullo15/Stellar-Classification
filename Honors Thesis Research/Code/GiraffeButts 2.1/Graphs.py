import matplotlib.pyplot as plt
import pandas as pd
import spectrum

pathtable = ["HD023643_20171211.txt", "HD120315_20170524.txt", "HD021071_20170109.txt"]
folder_path = "C:\\Users\\90rfa\\Documents\\data\\"
spectra = []
for name in pathtable:
        name = name.strip()
        table = pd.read_csv(folder_path+name, delim_whitespace = True)
        spectra.append(spectrum.Spectrum(table, name))

plt.plot(spectra[0].hydros[3].hydrodf["wv"], spectra[0].hydros[3].hydrodf["local"] +0.1)
plt.plot(spectra[1].hydros[3].hydrodf["wv"], spectra[1].hydros[3].hydrodf["local"] )
#plt.plot(spectra[2].hydros[3].hydrodf["wv"], spectra[2].hydros[3].hydrodf["local"] )

plt.show();

