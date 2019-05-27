#!/usr/bin/python
#
# spec_extract.py
#
# Routines for extracting a spectrum. Specifically designed for data
# taken with the Adams Observatory Lhires III long-slit spectrograph.
#
# List of Functions:
#  EXTRACT: This is the master program, and the only one that needs to be 
#   called during an extraction.
#  MDCOMBINE: Median-combine 2-D images
#  RNCALC: Calculate the read noise and gain from flat and bias images
#  FINDSRC: Finds the source in the dispersion direction by fitting a Gaussian
#  GAUSS_SKY: A Gaussian function with offset for FINDSRC
#  COLEXT_ONFLY: Extract the spectrum, performing a straight column extraction
#   with on-the-fly sky subtraction. Errors determined using the full CCD
#   equation.
#  FXDCOL: Fixed-width column extraction, used for extracting lamp spectra.
#
# Dependencies:
#  spec_rw
#  numpy
#  matplotlib.pyplot
#  scipy
#  time
#
# History:
#  DGW, 2016-05-10: Created and edited for brevity from the original, 
#   spec_redux_v2.py. These routines were originally written in spec_redux.py
#  DGW, 2016-05-13: Wavelength calibration spectrum is specified and 
#   included in data
#  DGW, 2016-10-21: Changed all numpy arithmetical operation calls to their 
#   NaN-excluding counterparts -- e.g.: numpy.nanmean, not numpy.mean; 
#   numpy.nansum, not numpy.sum; etc. See two notes: implement better way to 
#   normalize pixel values in final flat field; prob. remove NaN/Inf search
#   from FINDSRC
#  DGW, 2017-06-08: Compute bias level statistically using COMPUTEBIAS. Called
#   in EXTRACT, removes that single value from the dark, flat, and star 
#   images so that read noise is not compounded in final spectrum. Difference
#   appears to be negligible. Note: EXTREMELY SLOW! Commenting out until I can
#   sort out efficiency.
#
#  RBF, 2018-06-11: Removed the "plot as you go" functionality to increase 
#  		    the speed of testing.

import spec_rw as rw
import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
from scipy.ndimage import median_filter
import time

# N.B.: WANT TO MAKE BIASES AND FLATS OPTIONAL
# Function EXTRACT: Wrapper for the extraction routines that follow.
# Inputs:
#  SRCNAME: String name of the source being extracted
#  DATADIR: String path to data
#  SRCFILES: list of string source file names
#  BIASFILES: list of string bias file names
#  DARKFILES: list of string dark file names
#  FLATFILES: list of string flat file names. Biases and flats are used not 
#   only in data reduction but also for read noise and gain calcualtions.
#  EXPTIME: The exposure time -- used in finding dark current
#  WVFILES: optional list of string lamp files. If absent, the data spectra
#   are used to perform wavelength calibration.
#  FACTOR: How many sigmas around the peak the spectrum is extracted. Default 
#   is 2.
#  WRITECAL: Write out the master calibration files. Default is 'no'; can be
#   set to 'yes'.
#  USEFITS: Use curve_fit in FINDSRC ('yes') or else just maxval ('no'). Can 
#   be a list or else a single word
# Returns:
#  SPX_REDUX: tuple of dimensions [numelements,6,numspectra]. The six elements
#   are [wavelengths, raw spectrum, raw spectrum minus local sky, 
#        rectified spectrum, spectrum used for wavelength calibration (source 
#        or lamp), and signal-to-noise ratio]. The wavelengths and rectified
#   spectrum are not defined by SPEC_EXTRACT, but by SPEC_WAVECAL and
#   SPEC_CONTRECT respectively.
def extract(srcname,datadir,srcfiles,biasfiles,darkfiles,flatfiles,
            exptime,wvfiles=None,factor=2.,writecal='no',usefits='yes'):
    # Read in the data
    srcims  = rw.rdfitsmult(datadir,srcfiles)
    biasims = rw.rdfitsmult(datadir,biasfiles)
    darkims = rw.rdfitsmult(datadir,darkfiles)
    flatims = rw.rdfitsmult(datadir,flatfiles)
    if wvfiles != None:
        wvims = rw.rdfitsmult(datadir,wvfiles)

    # Array dimensions, number of images
    xsz     = srcims.shape[1]
    srcnum  = srcims.shape[2]
    flatnum = flatims.shape[2]
    if wvfiles != None:
        wvnum   = wvims.shape[2]

    # Reduce the source images
    	# master bias
    	#mbias = mdcombine(biasims)
    biasval = numpy.median(biasims)

    # Compute bias value and read noise in ADUs
    	#biasval,rdnoiseADU = computebias(biasims)

    # master dark
    mdark = mdcombine(darkims)

    # master flat (flat - bias)
    mflat = mdcombine(flatims) - biasval#mbias

    # normalize the flat -- this about gets the max val to 1.
    # DGW 2016-10-21: N.b. - There's a better way - see Birney, Chp. 9, p. 176
    flatsd = numpy.nanstd(mflat)
    flatnor = mflat / (numpy.median(mflat) + flatsd)

    # dark-subtract, flat-divide the science images
    finalims = numpy.zeros(srcims.shape).copy()
    loop_over = range(srcnum)
    for i in loop_over:
        temp = srcims[:,:,i]
        resu = (temp - mdark) / flatnor
        finalims[:,:,i] = resu

    # write the master calibration images to file in local directory
    if writecal == 'yes':
        flag = rw.wrtfitsngl(mbias,srcname+'_masterbias.fits')
        flag = rw.wrtfitsngl(mdark,srcname+'_masterdark.fits')
        flag = rw.wrtfitsngl(mflat,srcname+'_masterflat.fits')
        #for i in loop_over:
        #    flag = rw.wrtfitsngl(srcims[:,:,i],srcname+'_final'+str[i]+'.fits')
        print (srcims.shape)
        flag = rw.wrtfitsngl(srcims[:,:,0],srcname+'_final.fits')

    # Calculate the read noise and gain
    # printing several statistics during the run:
    print ('*************** For ',srcname,': ***************')
    rn,gain = rncalc(biasims,flatims)

    # calculate the average dark current
    drkim = (mdark - biasval) * gain # dark current + RN: e- per pixel
    	#ndrk  = (numpy.nanmean(drkim) - rn)/exptime # dark current: e-/s/pix
    ndrk  = (numpy.nanmean(drkim))/exptime # dark current: e-/s/pix
    print ('Dark Current = ',ndrk,'e- / second / pixel')

    # Begin the spectral extraction
    pixarr = numpy.arange(float(xsz))

    # extract each spectrum
    spx_redux = numpy.zeros((xsz,6,srcnum)).copy() # all data: wv, raw,  rms,
                                                   #          rect,wvcal,snr
    spx_raw = numpy.zeros((xsz,srcnum)).copy() # raw spectra
    spx_rms = numpy.zeros((xsz,srcnum)).copy() # raw - sky
    spx_rct = numpy.zeros((xsz,srcnum)).copy() # rectified spectra
    spx_snr = numpy.zeros((xsz,srcnum)).copy() # SNR ratio
    loop_over = range(srcnum)
    for i in loop_over:
        im = finalims[:,:,i]
        if usefits == 'yes': #len(usefits) == 1:
            answr = usefits
        else:
            answr = usefits[i]
        mn,sig = findsrc(im,finder=answr)
        spraw,sprms,spsnr = colext_onfly(im,rn,gain,ndrk,mn,sig,
                                         factor,exptime)
        spx_raw[:,i] = spraw
        spx_rms[:,i] = sprms
        spx_snr[:,i] = spsnr
        spx_redux[:,1,i] = spraw
        spx_redux[:,2,i] = sprms
        spx_redux[:,5,i] = spsnr
        if wvfiles == None:
            spx_redux[:,4,i] = sprms
        else:
            im = wvims[:,:,i]
            wvspec = fxdcol(im,mn,sig)
            spx_redux[:,4,i] = wvspec

    	#plt.figure()
    	#for i in loop_over:
    	#    plt.plot(spx_rms[:,i])
    	#plt.show(block=False)
    	#time.sleep(1)
    	#plt.close()
    return spx_redux

# Function MDCOMBINE: Median combine a 3-D array along the z-axis.
# Inputs:
#  IMARR: The 3-D image array. Individual images are in [x,y] plane, and these
#   images are stacked in the z-axis.
# Returns:
#  FINAL_IM: The final 3-D image.
def mdcombine(imarr):
    final_im = numpy.median(imarr,axis=2)
    return final_im

# Function COMPUTEBIAS: Using the bias images, plot a histogram of pixel 
#  values and fit a Gaussian to determine the bias value (mean) and read noise 
#  (one sigma) in ADUs.
# Input:
#  BIASIMS: The 3-D image array. Individual images are in [x,y] plane, and these
#   images are stacked in the z-axis.
# Returns:
#  BIASVAL: Bias value in ADUs
#  RDNOISE: Read noise in ADUs
def computebias(biasims):
    xsz = biasims.shape[0]
    ysz = biasims.shape[1]
    numbins = 41
    bimed   = numpy.median(biasims)
    bins    = numpy.arange(numbins)*5 + (bimed-50.)
    runningtotal = numpy.zeros((numbins-1)).copy()
    loopx = range(xsz)
    loopy = range(ysz)
    for i in loopx:
        for j in loopy:
            histb   = numpy.histogram(biasims[i,j,:],bins=bins)
            runningtotal = runningtotal + histb[0]
    loop = range(numbins-1)
    xarr = numpy.zeros((numbins-1)).copy()
    for i in loop:
        xarr[i] = histb[1][i] + (histb[1][i+1] - histb[1][i])
    norm_dist = runningtotal / max(runningtotal)
    idx = numpy.where(runningtotal == numpy.max(runningtotal))
    area = 1.0
    mx = xarr[int(idx[0][0])]
    sig = 2.0
    popt,pcov = curve_fit(gaus_nosky,xarr,norm_dist,p0=[area,mx,sig])
    return popt[1],popt[2]

# Function RNCALC: Calculate the read noise and gain using 3-D arrays of bias
#  and flat images. Follow calculations in Howell. I take the mean gain/read
#  noise for each image, and then finally take the mean of all of the 
#  final numbers to return
# Inputs:
#  BIASIMS: 3-D array of bias images. I typically take 20 bias images per night
#  FLATIMS: 3-D array of flat field images. I typically take at least 10
# Returns:
#  READNOISE: The average calculated read noise for the CCD chip
#  GAIN: The average calculated gain for the CCD chip
def rncalc(biasims,flatims):
    # Number of images
    numbias   = biasims.shape[2] - 1
    numflat   = flatims.shape[2] - 1
    # Create new arrays
    Gain      = numpy.zeros((numbias,numflat)).copy()
    ReadNoise = numpy.zeros((numbias,numflat)).copy()
    # Loop over all of the images
    loop_bias = range(numbias)
    loop_flat = range(numflat)
    for i in loop_bias:
        for j in loop_flat:
            b1 = biasims[:,:,i]
            b1mn = numpy.nanmean(b1)
            b2 = biasims[:,:,i+1]
            b2mn = numpy.nanmean(b2)
            f1 = flatims[:,:,j]
            f1mn = numpy.nanmean(f1)
            f2 = flatims[:,:,j+1]
            f2mn = numpy.nanmean(f2)
            b1b2 = b1 - b2
            f1f2 = f1 - f2
            b1b2std = numpy.nanstd(b1b2)
            f1f2std = numpy.nanstd(f1f2)
            Gain[i,j] = ((f1mn + f2mn) - (b1mn + b2mn)) / \
                        (f1f2std**2 - b1b2std**2)
            ReadNoise[i,j] = Gain[i,j] * b1b2std / numpy.sqrt(2)
    print ('Gain       =  '+"{:.4}".format(numpy.nanmean(Gain))+' e-/ADU')
    print ('Read Noise = '+"{:.4}".format(numpy.nanmean(ReadNoise))+' e-/pixel')
    return numpy.nanmean(ReadNoise),numpy.nanmean(Gain)

# Function FINDSRC: Collapse the spectrum and find the peak in the dispersion
#  direction using a Gaussian fit.
# Input:
#  IM: The spectrum image
#  USEFIT: Use the fitter ('yes') or else use maxval ('no'). Default is 'yes'
# Returns:
#  MN: The mean position in the dispersion direction
#  SG: The sigma of the Gaussian fit to the source dispersion
def findsrc(im,finder='yes'):
    # Median-filtering the image before performing the trace gets rid of some
    #  of the highest-valued pixels at the edges of the array, which are most
    #  prevalent for long exposure times.
    im2 = median_filter(im,size=(5,5))
    trace = numpy.median(im2,axis=1)
    # Get rid of any NaNs or Infs, since they screw with curve_fit
    # DGW 2016-10-21: This may have been solved by calling nanmedian above
    temp = numpy.zeros(trace.shape[0])
    temp = trace[~numpy.isnan(trace)]
    temp = temp[~numpy.isinf(temp)]
    trace = temp
    #plt.figure()
    #plt.plot(trace)
    #plt.show()#block=False)
    #time.sleep(1.0)
    #plt.close()
    num = trace.shape[0]
    numarr = numpy.arange(num)
    idx = numpy.where(trace == numpy.max(trace))
    mx = int(idx[0][0])
    mn= 0
    sg = 0
    print ('Pixel with highest value = ',mx)
    if finder == 'yes':
        sig = 3.0
        offset = 1.0
        area = 1000.0
        try:
            popt,pcov = curve_fit(gaus_sky,numarr,trace,p0=[area,mx,sig,offset])
            if abs(popt[1]-mx) >= 5.0:
            	mn = mx
            	sg = sig
            else:
            	mn = popt[1]
            	sg = popt[2]
            #plt.figure()
       	    #plt.title('Gaussian fit to dispersion')
       	    #plt.plot(numarr,trace)
       	    #plt.plot(numarr,gaus_sky(numarr,popt[0],mn,popt[2],popt[3]))
       	    #plt.show(block=False)
       	    #time.sleep(0.5)
       	    #plt.close()
        except:
            print("Whoops!")

    else:
        mn = mx
        sg = 3.0
    print ('Mean and width of fit    = ',mn,sg)
    return mn,abs(sg)

# Function GAUS_SKY: a Gaussian function superposed on a continuum,
#  called by findsrc
# Inputs:
#  X: dispersion pixel values
#  A: area under the Gaussian curve
#  X0: mean of Gaussian
#  SIGMA: standard deviation of the Gaussian
#  CONT: A continuum over which the Gaussian sits
def gaus_sky(x,a,x0,sigma,cont):
    return cont + a*exp(-(x-x0)**2/(2*sigma**2))

# Function GAUS_NOSKY: a Gaussian function without continuum, called by
#  COMPUTEBIAS
# Inputs:
#  X: dispersion pixel values
#  A: area under the Gaussian curve
#  X0: mean of Gaussian
#  SIGMA: standard deviation of the Gaussian
def gaus_nosky(x,a,x0,sigma):
    return a*exp(-(x-x0)**2/(2*sigma**2))
                
# Function: COLEXT_ONFLY: A column extraction of the spectrum from the source
#  image, with on-the-fly sky subtraction at each wavelength bin. Errors
#  propagated by means of the CCD equation.
# Inputs:
#  IM: The image that the spectrum is to be extracted from
#  RN: The CCD chip read noise
#  GAIN: The CCD chip gain
#  NDRK: The dark current per unit time
#  MEAN: The spectral dispersion mean
#  SIGMA: The spectral dispersion width
#  FACTOR: A multiplicative factor of the dispersion width that decides the
#   extraction width
#  SKYWDTH: The width of the sky window on either side of the spectrum
#  SEP: The separation between the spectral extraction window and sky
#   extraction window
# Returns:
#  SPRAW: The raw extracted spectrum
#  SPRMS: The raw-minus-sky extracted spectrum
#  SPSNR: The signal-to-noise ratio for each wavelength bin
def colext_onfly(im,rn,gain,ndrk,mean,sigma,factor,exptime,
                 skywdth=50.,sep=10.):
    # size of the array
    xsz = im.shape[0]
    ysz = im.shape[1]
    # the 1-D spectrum will be written here:
    spraw = numpy.zeros(ysz).copy()
    sprms = numpy.zeros(ysz).copy()
    spsnr = numpy.zeros(ysz).copy()
    # loop over every row
    loop_over = range(ysz)
    for i in loop_over:
        # choose the extraction window
        peak = int(mean)
        lo = peak - int(factor*sigma)
        hi = peak + int(factor*sigma)
        diff = hi - lo
        # choose the sky windows
        sky1lo = lo - sep - skywdth
        sky1hi = lo - sep
        sky2lo = hi + sep
        sky2hi = hi + sep + skywdth
        # compute the sky values
        sky1    = im[int(sky1lo):int(sky1hi),i]
        sky1val = numpy.nanmean(sky1)
        sky2    = im[int(sky2lo):int(sky2hi),i]
        sky2val = numpy.nanmean(sky2)
        skyval  = (sky1val + sky2val)/2 # per pixel
        # compute the star - sky, in electrons
        rawval = numpy.nansum(im[lo:hi,i]) * gain
        rmsval = (numpy.nansum(im[lo:hi,i]) - (skyval*diff)) * gain
        # compute the star error in electrons from the CCD equation 
        #  (Howell, p. 75)
        valerr = numpy.sqrt(rmsval + (diff * (1.+diff/(skywdth*2)) * \
                                      (skyval*gain + 
                                       ndrk*exptime + 
                                       rn**2 + 
                                       (gain**2 * 0.289**2))))
        spraw[i] = rawval
        sprms[i] = rmsval
        spsnr[i] = rmsval/valerr # the S/N
    print ('sqrt(N*)    = ',numpy.sqrt(numpy.nanmean(sprms)),' (Poisson noise only)')
    print ('Actual S/N  = ',numpy.nanmean(spsnr),' (full CCD equation)')
    return spraw,sprms,spsnr

# Function FXDCOL: extract a spectrum between fixed positions in the
#  dispersion direction
# Inputs:
#  IM: the 2-D image
#  MEAN: the mean value, as determined using findsrc
#  SIGMA: the sigma value, as determined using findsrc
#  FACTOR: passed from extract (or else set), how many sigma around the mean 
#   you wish to extract
# Returns:
#  lamp1d: the 1-D lamp spectrum
def fxdcol(im,mean,sigma,factor=2.0):
    # size of the array
    xsz = im.shape[0]
    ysz = im.shape[1]
    # define the lox and hix values
    lox = int(mean) - int(factor * sigma)
    hix = int(mean) + int(factor * sigma)
    # the 1-D spectrum will be written here:
    lamp1d = numpy.zeros(ysz).copy()
    # loop over every row
    loop_over = range(ysz)
    for i in loop_over:
        val = numpy.nansum(im[lox:hix,i])
        lamp1d[i] = val
    return lamp1d
