#!/usr/bin/python
#
# spec_rw.py
#
# Read and write routines used when reducing spectra. Specifically
# designed for data taken with the Adams Observatory Lhires III
# long-slit spectrograph.
#
# List of Functions:
#  RDFITSNGL: Reads a single 2-D FITS image file
#  RDFITSMULT: Read a list of 2-D FITS image files
#  RDFITSHEAD: Read in the FITS headers of a list of FITS files
#  WRTFITSNGL: Write a single 2-D FITS image to file
#  READSPEC: Read an ASCII file of between 2 and 10 columns
#  WRTSPEC: Write an ASCII file of a reduced spectrum, 6 columns (see below)
#  PLOTSNGLSPEC: Write a single spectrum to an EPS plot
#
# Dependencies:
#  pyfits
#  numpy
#  asciitable
#  matplotlib (for PLOTSNGLSPEC)
#
# History:
#  DGW, 2016-05-10: re-written from the original, spec_redux.py
#  DGW, 2016-05-13: edited WRTSPEC to include a sixth column (wvcal)
#  DGW, 2016-06-14: edited READSPEC to read as many as 15 columns
#  DGW, 2016-10-24: Included PLOTSNGLSPEC from old spec_redux.py module
#  DGW, 2017-10-17: Wrote RDFITSHEAD
#

import pyfits
import numpy
import asciitable
import matplotlib.pyplot as plt

# Function RDFITSNGL: Read a single 2-D FITS image file using pyfits.
#  DIR: string directory path
#  IM: string FITS image name
# Returns: a 2-D array with the image data
def rdfitsngl(dir,im):
    hdulist = pyfits.open(dir+im)
    data = hdulist[0].data
    return data

# Function RDFITSMULT: Read in 2-D FITS images from a list.
#  DIR: string directory path
#  LIST: string list of 2-D FITS image names
# Returns: a 3-D array of 2-D images; Z-axis length is length of list
def rdfitsmult(dir,list):
    numims = len(list)
    # Open a test image to determine image dimensions
    hdulist = pyfits.open(dir+list[0], ignore_missing_end=True)
    data = hdulist[0].data
    xsz = data.shape[0]
    ysz = data.shape[1]
    # Create the data array
    imarr = numpy.zeros((xsz,ysz,numims)).copy()
    loop_over = range(numims)
    for i in loop_over:
        hdulist = pyfits.open(dir+list[i], ignore_missing_end=True)
        data    = hdulist[0].data
        imarr[:,:,i] = data
    return imarr

# Function RDFITSHEAD: Read in FITS image headers from a list.
#  DIR: string directory path
#  LIST: string list of 2-D FITS image names
# Returns: headers for each FITS image
def rdfitshead(dir,list):
    numims = len(list)
    # Open a test image to determine image dimensions
    hdulist = pyfits.open(dir+list[0], ignore_missing_end = True)
    header = hdulist[0].header
    headlength = len(header)
    # Create the list of headers
    headlst = ["" for x in range(len(list))]
    loop_over = range(numims)
    for i in loop_over:
        hdulist = pyfits.open(dir+list[i], ignore_missing_end = True)
        header  = hdulist[0].header
        #headarr[:,i] = header
        headlst [i] = header
    return headlst

# Function WRTFITSNGL: Writes out single FITS image, dimensions unspecified
#  IMAGE: the image array
#  NAME: string name for output -- can include directory path
# Returns: a flag valued 1
def wrtfitsngl(image,name):
    hdu = pyfits.PrimaryHDU(image)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(name)
    flag = 1
    return flag

# Function READSPEC: reads in an ASCII txt format spectrum using numpy
#  FILENAME: the .txt file to read in
#  NSKIP: the number of rows to skip at beginning of file (header length)
# Returns: the data, separated into columns (2 MIN, 15 MAX)
def readspec(filename,nskip):
    data = numpy.loadtxt(filename,skiprows=nskip)
    ncols = data.shape[1]
    # Assign column variables
    if ncols >= 2:
        d1 = data[:,0]
        d2 = data[:,1]
    if ncols >= 3:
        d3 = data[:,2]
    if ncols >= 4:
        d4 = data[:,3]
    if ncols >= 5:
        d5 = data[:,4]
    if ncols >= 6:
        d6 = data[:,5]
    if ncols >= 7:
        d7 = data[:,6]
    if ncols >= 8:
        d8 = data[:,7]
    if ncols >= 9:
        d9 = data[:,8]
    if ncols >=10:
        d10= data[:,9]
    if ncols >=11:
        d11= data[:,10]
    if ncols >=12:
        d12= data[:,11]
    if ncols >=13:
        d13 = data[:,12]
    if ncols >=14:
        d14 = data[:,13]
    if ncols >=15:
        d15 = data[:,14]
    # Return the results
    if ncols == 2:
        return d1,d2
    if ncols == 3:
        return d1,d2,d3
    if ncols == 4:
        return d1,d2,d3,d4
    if ncols == 5:
        return d1,d2,d3,d4,d5
    if ncols == 6:
        return d1,d2,d3,d4,d5,d6
    if ncols == 7:
        return d1,d2,d3,d4,d5,d6,d7
    if ncols == 8:
        return d1,d2,d3,d4,d5,d6,d7,d8
    if ncols == 9:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9
    if ncols == 10:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10
    if ncols == 11:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11
    if ncols == 12:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12
    if ncols == 13:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13
    if ncols == 14:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14
    if ncols == 15:
        return d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15

# Function WRTSPEC: writes out a reduced spec in ASCII format
# N.B.: WANT TO INCLUDE A HEADER
#  SPEX: Output spectra from extract/wvcal/contrect
#  NAMES: column names
#  FILENAMES: what to call them
# Returns: a flag of value 1
def wrtspec(spex,names,filenames):
    numcols = spex.shape[1]
    numsp   = spex.shape[2]
    n1 = names[0]
    n2 = names[1]
    n3 = names[2]
    n4 = names[3]
    n5 = names[4]
    n6 = names[5]
    loop_over = range(numsp)
    for i in loop_over:
        asciitable.write({n1:spex[:,0,i],n2:spex[:,1,i],n3:spex[:,2,i],
                          n4:spex[:,3,i],n5:spex[:,4,i],n6:spex[:,5,i]},
                         filenames[i],names=names)
    flag = 1
    return flag

# Function plotsnglspec: plot a single spectrum in .eps format
#  wv: the wavelength array
#  sp: the extracted spectrum
#  figxsz: the int x-size of the figure
#  figysz: the int y-size of the figure
#  xlabel: the string label on the x-axis
#  ylabel: the string label on the y-axis
#  filename: the string filename (must include .eps)
#  yscale: optional input, axis scale defaults to linear, but could be 'log'
def plotsnglspec(wv,sp,wvmin,wvmax,spmin,spmax,
                 figxsz,figysz,xlabel,ylabel,filename,yscale='linear'):
   
    fig = plt.figure(figsize=(figxsz,figysz))
    
    ax1 = fig.add_subplot(111,autoscale_on=False,xlim=(wvmin,wvmax),
                          ylim=(spmin,spmax))
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_yscale(yscale)
    ax1.plot(wv,sp,'k-')
    plt.savefig(filename,dpi=200,facecolor='w',edgecolor='w',
                orientation='portrait',transparent='False',format='eps')
    plt.close(fig)
    flag = 1
    return flag
