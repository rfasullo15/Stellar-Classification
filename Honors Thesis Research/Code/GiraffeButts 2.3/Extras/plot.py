import numpy as np
import matplotlib.pyplot as plt

# Take a spectrum
datadir = '/home/dwhelan/analysis/OBA_AO/data/'
spec=np.loadtxt(datadir+'HD172167_20180702.txt',skiprows=1)

# Make a new array of the same dimensions
spec_w_noise = np.zeros((spec.shape)).copy()

# Put in the original wavelength values:
spec_w_noise[:,0] = spec[:,0]

# Perturb the rms spectrum
for i in range(spec.shape[0]):
    randnum = np.random.normal(loc=spec[i,2],scale=0.03*spec[i,2])
    spec_w_noise[i,2] = randnum

# Now, overplot the two:
plt.figure()
plt.plot(spec[:,0],spec[:,2])
plt.plot(spec_w_noise[:,0],spec_w_noise[:,2])
plt.show(block=False)
