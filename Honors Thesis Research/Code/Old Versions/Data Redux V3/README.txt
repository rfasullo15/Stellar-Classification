Data Reduction Tutorial
-----------------------
7 May, 2018, DGW

-----------------------------OVERVIEW---------------------------------

In the gzipped tar file called DataReduxTut_20180410.tar.gz, you will
find a number of pieces of code, plus a dataset, to familiarize
yourself with spectroscopic data reduction.

You will find it useful to reference Howell's Handbook of CCD
Astronomy to understand the technical terms used below.

-----------------------------END: OVERVIEW----------------------------

-----------------------------AO_REDUX---------------------------------

Begin with the python script: ao_redux.py. When you are eventually
ready to run this script, you will do so by typing

$ python ao_redux.py

at the command prompt. For now, simply open it with a text editor.

You have four dependencies listed at the top of the script:
- spexredux: The module that controls spectral reduction and extraction
- matplotlib.pyplot: The plotting module most frequently used
- numpy: Contains a number of indispensible functions
- spec_type: A program for comparing spectra of target stars against
  spectra of stars with known spectral type. This so-called spectral
  classification is the most fundamental research tool that you will
  be working with, upon which most of our other work will depend.

Then, you have a bunch of lists and additional parameters defined:
- datadir: The directory containing the data directory, ./2018-04-10/
- imfiles: A list of the names of the FIT image files
- srcnames: A list containing the string names of the sources
- lamp: A file or files containing images of the spectral calibration
  NeAr emission lamp
- flat: A list of flatfield images
- bias: A list of bias images
- alldarks: Embedded lists of all of the dark current images taken,
  for each of the exposure times.
- darkexptimes: A list of the exposure times for the images in alldarks
- wvs: A list of the wavelengths of the Balmer lines in the stellar
  spectra, starting with Hbeta

The next line of the code calls the program `extract' in the spexredux
module. This code computes the gain and read noise, reduces the source
images with the flatfield, bias, and dark current images, finds the
trace of the spectrum on the image, extracts the spectrum and
propagates uncertainties in terms of the signal-to-noise ratio, then
presents you with an extracted spectrum in a GUI (courtesy of
matplotlib). You will use the mouse to identify the centers of the
first five Balmer absorption lines. When you have done so, following
the (scant) directions on the screen, you will close the window. This
wavelength calibration will be done for all sources, and then you will
be required to choose continuum points unaffected by absorption lines
in order to rectify the spectrum -- again, use the directions
provided.

Once all spectra have been reduced, extracted, calibrated, and
rectified, they will be written to file in the current directory as
ASCII files. The first column of each file will include the wavelength
values for each spectral element, the second will be the raw,
extracted spectrum, the third column will be the raw spectrum minus
the contamination from the sky, the fourth will be the rectified
spectrum, the fifth will be the NeAr lamp spectrum, and the sixth will
be the signal-to-noise ratio values.

Lastly, spec_type is called in order to assist you with spectral
typing. To get you started, refer to ``A Digital Spectral
Classification Atlas'':
https://ned.ipac.caltech.edu/level5/Gray/frames.html. As you become
more advanced, you will begin to rely more heavily on the book,
``Stellar Spectral Classification'' by Gray & Corbally.

-----------------------------END: AO_REDUX----------------------------

-----------------------------THE REST OF THE CODE---------------------

Now that you have a basic idea of what the code does, take a look into
spexredux.py. You will see that this code is really a wrapper for the
more meaty modules that actually perform the image reduction and
spectral extraction tasks: 

- spec_rw for reading and writing FITS and ASCII files
- spec_extract for performing spectral extractions
- spec_wavecal for performing wavelength calibration
- spec_contrect_spline for performing continuum rectification

as well as scipy (stats), matplotlib, and time. The code for
``extract'' is fairly well commented, and should give you a basic idea
of what is actually being done when. From here, you can follow the
code through all the modules to learn how each part operates.

-----------------------------END: THE REST OF THE CODE----------------

-----------------------------GETTING STARTED--------------------------

(1) Choose directory locations for your code, data, and
documentation. Make sure that python knows where your code is
located. Here is my python path set in my .bashrc file:

# add my python modules directory to the PYTHONPATH:
export PYTHONPATH=$PYTHOPATH:/home/dwhelan/code/python/modules

Keep the code, raw data, and data products separate.

Make sure your raw data are read-only, so that you don't lose them by
mistake.

Make an entire directory tree that is merely dedicated to data
reduction. That way there is never any confusion between raw and
reduced data products, since they exist in separate places.

(2) Look at your 2-D images. Download the SAO DS9 image viewer, and
use it to open each and every single raw data image to check for
problems. (I understand that you won't know problematic data to start
with, but begin this habit of checking now so that future issues don't
ever pass you by unwitting.)

(3) Run ao_redux.py, follow the steps, and produce your first dataset!
Have fun spectral typing; do the best you can, and we'll discuss the
results when you've got them.

(4) To plot one of your spectra at a later date, follow these steps in
python:

$ import numpy as np
$ import matplotlib.pyplot as plt
$ spec = np.loadtxt('StarName.txt',skiprows=1)
$ plt.figure()
$ plt.plot(spec[:,0],spec[:,3])
$ plt.xlabel(r'$\lambda$ ($\AA$)')
$ plt.ylabel('Rectified Intensity')
$ plt.title('Optical Spectrum of SpecName')
$ plt.show(block=False)

...and then use the buttons in the matplotlib GUI to play with your spectrum.

You can overplot multiple spectra in this way by substituting the
following for the plt.plot() command:

$ plt.plot(spec1[:,0],spec1[:,3])
$ plt.plot(spec2[:,0],spec2[:,3])

Or you can plot them with a vertical offset to compare spectral features:

$ plt.plot(spec1[:,0],spec1[:,3])
$ plt.plot(spec2[:,0],spec2[:,3]+0.4)

You can even set the line color, width, font size of axis labels; you
can insert text on the plot, make multiple plots simultaneously; the
possibilities are practically limitless, and the documentation for
matplotlib should become very familiar to you: https://matplotlib.org/

-----------------------------END: GETTING STARTED---------------------

-----------------------------MOVING FORWARD---------------------------

Once you have learned to reduce your spectra and perform a spectral
classification, you are ready to use these tools to pursue questions
of astronomical interest.

Do not hesitate to contact me for assistance! But please remember that
I am not an IT specialist; these programs were all written for my lab
Linux boxes, and compatibility issues may exist. I can help to
troubleshoot such issues, but my true abilities lie in dealing with
instrumentation, data, and astronomical inquiries.

-----------------------------END: MOVING FORWARD----------------------
