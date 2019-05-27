#/usr/bin/python
#
# spexredux.py
#
# A wrapper that reduces an entire night's set of data.
#
# List of functions:
#  EXTRACT: This is the only program
#
# Dependencies:
#  spec_rw
#  spec_extract
#  spec_wavecal
#  spec_contrect_spline
#  numpy
#  scipy.stats
#  matplotlib
#  time
#
# History:
#  DGW, 2017-10-17: Written, based largely on spec_extract.py's EXTRACT 
#    routine plus subsequent calibration steps.
#  RBF, 2018-6-17: Removed the "plot as you go" feature

# Import:

import spec_rw as rw
import spec_extract as ext
import spec_wavecal as wcal
import spec_contrect_spline as rect
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time

# Function EXTRACT: Extract a list of spectra and return the extracted
# spectra to file.
# Input:
#  DATADIR: The data directory
#  SRCNAMES: A list of source names, corresponding to files given in SRCFILES
#  SRCFILES: A list of source FITS files in DATADIR
#  BIASFILES: A list of bias FITS files in DATADIR
#  FLATFILES: A list of flat FITS files in DATADIR
#  ALLDARKS: A 2-D list of dark current FITS files: alldarks[numdarks,exptimes]
#  DARKEXPTIMES: The exposure times corresponding to the different sets of 
#    dark files used (PROBLEM: What if no darks were taken?)
#  WVFILES: Optional keyword, a list of wavelength calibration FITS files in
#    DATADIR
#  WVVALS: The wavelengths to be used in wavelength calibration
#  EXTWDTHFACTOR: How many sigma around the mean to extract
#  WRITECAL: Default is 'no', state whether you want final calibration images
#    to be output to FITS file
#  USEFITS: State whether you want to make a fit to the dispersion to compute 
#    the signal width, sigma. Default is 'yes', but will set a value 
#    of sigma=3.0 if set to 'no'
#  AUTORECT: If 'no', then manual rectification will be required. If 'yes', 
#    then a cubic spline is fit to the continuum, as defined in 
#    spec_contrect_spline.py
def extract(datadir,srcnames,srcfiles,biasfiles,flatfiles,alldarks,
            darkexptimes,wvfiles=None,wvvals=[4861.,4341.,4102.,3970.,3889.],
            extwdthfactor=2.,writecal='no',usefits='yes',autorect='no'):

    # Read in the data
    srcims     = rw.rdfitsmult(datadir,srcfiles)
    srcheaders = rw.rdfitshead(datadir,srcfiles)
    biasims    = rw.rdfitsmult(datadir,biasfiles)
    flatims    = rw.rdfitsmult(datadir,flatfiles)

    # Required: Each set of darks has the same number of exposures
    numdrkexpt = len(darkexptimes)
    numdarkframes = len(alldarks[0])
    darkims = np.zeros((srcims.shape[0],srcims.shape[1],numdarkframes,numdrkexpt)).copy()
    for i in range(numdrkexpt):
        temp = rw.rdfitsmult(datadir,alldarks[i])
        darkims[:,:,:,i] = temp
    if wvfiles != None:
        wvims = rw.rdfitsmult(datadir,wvfiles)

    # Array dimensions, number of source images
    xsz    = srcims.shape[1]
    srcnum = srcims.shape[2]
    if wvfiles != None:
        wvnum = wvims.shape[2]

    # A list of the exposure times for each source image
    exptimes = np.zeros(srcnum).copy()
    for i in range(srcnum):
        exptimes[i] = srcheaders[i]['EXPTIME']

#***Reduce the source images***#

    # Determine the bias value
    biasval = np.median(biasims)

    # Compute master dark frames per exposure time
    mdarks  = np.zeros((srcims.shape[0],srcims.shape[1],numdrkexpt)).copy()
    for i in range(numdrkexpt):
        temp          = ext.mdcombine(darkims[:,:,:,i])
        mdarks[:,:,i] = temp

    # Calculate the normalized flatfield
    mflat = ext.mdcombine(flatims) - biasval
    flatnor = mflat / stats.mode(mflat,axis=None)[0][0]
    # Write out calibration files, if desired
    if writecal == 'yes':
        flag = rw.wrtfitsngl(flatnor,datadir+'masterflat.fits')
        for i in range(numdrkexpt):
            flag = rw.wrtfitsngl(mdarks[:,:,i],datadir+'masterdark'+str(darkexptimes[i])+'s.fits')

    # Reduce the source images
    finalims = np.zeros(srcims.shape).copy()
    for i in range(srcnum):

        # Determine whether we should be subtracting dark images or biases
        expt = exptimes[i]
        idx = np.array(np.nonzero((np.asarray(darkexptimes) == expt))).reshape(-1).tolist()
        if not idx:
            tempdark = biasval
        else:
            tempdark = mdarks[:,:,idx[0]]
        temp = srcims[:,:,i]
        resu = (temp - tempdark) / flatnor
        finalims[:,:,i] = resu

    # Calculate the read noise and gain
    rn,gain = ext.rncalc(biasims,flatims)

    # Calculate the average dark current
    ndrk = (np.median((np.nan_to_num(tempdark)-biasval)*gain))/exptimes[i]
    print ('dark current = ' + "{:.4}".format(ndrk) + 'e-/s')

#***Spectral Extraction***#

    # initialize reduction array
    spx_redux = np.zeros((xsz,6,srcnum)).copy() # all data: wv,raw,rms,rect,wvcal,snr

    # Extract each spectrum
    loop_over = range(srcnum)
    for i in loop_over:
        im = finalims[:,:,i]

        # Determine if we are fitting to the dispersion
        if usefits == 'yes':
            answr = usefits
        else:
            answr = usefits[i]

        # Find the source in the dispersion direction
        mn,sig = ext.findsrc(im,finder=answr)

        # Extract the spectrum with an on-the-fly background subtraction
        spraw,sprms,spsnr = ext.colext_onfly(im,rn,gain,ndrk,mn,sig,extwdthfactor,exptimes[i])
        spx_redux[:,1,i] = spraw
        spx_redux[:,2,i] = sprms
        spx_redux[:,5,i] = spsnr
        
      
#***Wavelength calibration***#

    for i in loop_over:
        # Find out which spectrum to use
        if wvfiles == None:
            spx_redux[:,4,i] = spx_redux[:,2,i]
        elif len(wvfiles) == 1:
            im = wvims[:,:,0]
            wvspec = ext.fxdcol(im,mn,sig)
            spx_redux[:,4,i] = spx_redux[:,2,i]
        else:
            im = wvims[:,:,i]
            wvspec = ext.fxdcol(im,mn,sig)
            spx_redux[:,4,i] = wvspec

    # Perform the wavelength calibration
    spec_w = wcal.wavecal(spx_redux, wvvals, srcnames = srcnames)

    # For one wavecal image, substitute the cal lamp spectrum into spx_redux
    if len(wvfiles) == 1:
        for i in loop_over:
            spx_redux[:,4,i] = wvspec

#***Continuum rectification***#
    spec_r = rect.rect(spx_redux, auto=autorect, window=3.0)

    # Record the data
    colnames = ['wv','raw','rms','rect','wvcal','snr']
    flag     = rw.wrtspec(spx_redux, colnames, [s+'.txt' for s in srcnames])
    
    # Return the extracted spectra
    return spx_redux
