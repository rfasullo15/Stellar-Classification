#!/usr/bin/python
#
# spec_type.py
#
# A class that provides a GUI for comparing gold standard spectra to
# target spectra -- a GUI-based spectral-typing assistance tool,
# designed specifically for late O-, all B- and A-type stars.
#
# Because I have not yet finished my observations of the gold standard
# stars, this first version supplements AO gold standard spectra with
# spectra taken from  MKCLASS's libr18, which is
# sampled at a close match of 0.5A dispersion, but only from
# 3800-4620. (NOTE: May need to transition to libnor36, with 1A dispersion 
# sampled from 3800-5600, depending both on the wavelength coverage advantage 
# and that stars up to O6 are used in that library).
#
# Class SPTYPE:
#
# __INIT__: The main program plots the target spectrum along with (by
#  default) B5V and B7V stars on either side. To alter the standard star
#  spectra shown requires one of the keystrokes described below.
# ONTYPE: A subroutine with the possible keystrokes that will alter the plot.
#  RIGHTARROW: Will transition from showing the current luminosity class to 
#   showing the next highest luminosity class for the given spectral types.
#  LEFTARROW: Will transition back from showing higher to lower luminosity 
#   classes.
#  UPARROW: Will plot the next earliest spectral type for the given luminosity 
#   class.
#  DOWNARROW: Will plot the next latest spectral type for the given luminosity
#   class.
#
# Dependencies: numpy, pylab
#
# History:
#  DGW, 4 Dec 2017: Written
#  DGW, 13 Dec 2017: Added O9.5, B0.5, B1.5, B2.5, A5, A7, and A9 classes
#                    Updated gold standards list
#                    Altered color scheme for spectra: black for source, red for
#                     gold standards
#  DGW, 3 Mar 2018: Comparing to only one source at a time, offset by only 0.1
#                    for close comparison of Balmer lines
#  DGW, 21 Mar 2018: Two plots: One an overplot, one a comparison to two 
#                     standards

import numpy as np
import pylab as plt

class sptype:

    # __INIT__
    # Inputs:
    #  WV: Wavelengths for target spectrum
    #  SPEC: Rectified intensities of target spectrum
    #  SRCNAME: Source name, as a string
    def __init__(self, wv, spec, srcname):
        # Read in the gold standard spectra
        self.goldstds = None
        self.goldsptypes = None
        self.wv = wv
        self.spec = spec
        self.srcname = srcname
        self.goldstds,self.goldsptypes = self.readgolds()
        # Plot the target spectrum and first comparisons (B5V and B7V)
        # B5V and B7V indices:
        self.lumi = 0 # Luminosity class V
        self.sp1i = 9 # sp1 will always be earlier type
        self.sp2i = 10 # sp2 will always be later type
        fig = plt.figure()
        self.ax = fig.add_subplot(111,frameon=False)
        self.ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        self.ax.grid(False)
        self.ax.set_xlabel(r'$\lambda$ ($\AA$)')
        self.ax.set_ylabel('Rectified Intensity + Offset')
        self.ax1 = fig.add_subplot(211)
        self.ax1.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
        self.ax1.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
        self.ax1.plot(self.wv,self.spec+0.4,'k-')
        self.ax1.text(4500,1.45,self.srcname)
        self.ax1.plot(self.goldstds[:,0,self.sp1i,self.lumi],self.goldstds[:,1,self.sp1i,self.lumi]+0.8,'r-')
        self.ax1.text(4500,1.85,self.goldsptypes[self.sp1i][self.lumi])
        self.ax2 = fig.add_subplot(212)
        self.ax2.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
        self.ax2.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
        self.ax2.plot(self.wv,self.spec,'k-')
        self.ax2.text(4500,1.05,self.srcname)        
        self.ax1.set_title('Spectral Typing '+self.srcname)
        self.ax1.axis((3850,4600,0,2.0))
        self.ax2.axis((3850,4600,0,1.2))
        fig.canvas.mpl_connect('key_press_event',self.ontype)
        plt.show()

    # ONTYPE: Use arrow keys to plot different spectra
    def ontype(self, event):
        if event.key == 'up':
            # Clear the plot
            self.ax.cla()
            self.ax1.cla()
            self.ax2.cla()
            # Earlier spectral types
            self.sp1i = self.sp1i - 1
            self.sp2i = self.sp2i - 1
            self.ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
            self.ax.grid(False)
            self.ax.set_xlabel(r'$\lambda$ ($\AA$)')
            self.ax.set_ylabel('Rectified Intensity + Offset')
            self.ax1.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax1.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax1.plot(self.wv,self.spec+0.4,'k-')
            self.ax1.text(4500,1.45,self.srcname)
            self.ax1.plot(self.goldstds[:,0,self.sp1i,self.lumi],self.goldstds[:,1,self.sp1i,self.lumi]+0.8,'r-')
            self.ax1.text(4500,1.85,self.goldsptypes[self.sp1i][self.lumi])
            self.ax2.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax2.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax2.plot(self.wv,self.spec,'k-')
            self.ax2.text(4500,1.05,self.srcname)        
            self.ax1.set_title('Spectral Typing '+self.srcname)
            self.ax1.axis((3850,4600,0,2.0))
            self.ax2.axis((3850,4600,0,1.2))
            plt.draw()

        if event.key == 'down':
            # Clear the plot
            self.ax.cla()
            self.ax1.cla()
            self.ax2.cla()
            # Later spectral types
            self.sp1i = self.sp1i + 1
            self.sp2i = self.sp2i + 1
            self.ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
            self.ax.grid(False)
            self.ax.set_xlabel(r'$\lambda$ ($\AA$)')
            self.ax.set_ylabel('Rectified Intensity + Offset')
            self.ax1.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax1.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax1.plot(self.wv,self.spec+0.4,'k-')
            self.ax1.text(4500,1.45,self.srcname)
            self.ax1.plot(self.goldstds[:,0,self.sp1i,self.lumi],self.goldstds[:,1,self.sp1i,self.lumi]+0.8,'r-')
            self.ax1.text(4500,1.85,self.goldsptypes[self.sp1i][self.lumi])
            self.ax2.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax2.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax2.plot(self.wv,self.spec,'k-')
            self.ax2.text(4500,1.05,self.srcname)        
            self.ax1.set_title('Spectral Typing '+self.srcname)
            self.ax1.axis((3850,4600,0,2.0))
            self.ax2.axis((3850,4600,0,1.2))
            plt.draw()

        if event.key == 'left':
            # Clear the plot
            self.ax.cla()
            self.ax1.cla()
            self.ax2.cla()
            # Lower luminosity class
            self.lumi = self.lumi - 1
            self.ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
            self.ax.grid(False)
            self.ax.set_xlabel(r'$\lambda$ ($\AA$)')
            self.ax.set_ylabel('Rectified Intensity + Offset')
            self.ax1.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax1.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax1.plot(self.wv,self.spec+0.4,'k-')
            self.ax1.text(4500,1.45,self.srcname)
            self.ax1.plot(self.goldstds[:,0,self.sp1i,self.lumi],self.goldstds[:,1,self.sp1i,self.lumi]+0.8,'r-')
            self.ax1.text(4500,1.85,self.goldsptypes[self.sp1i][self.lumi])
            self.ax2.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax2.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax2.plot(self.wv,self.spec,'k-')
            self.ax2.text(4500,1.05,self.srcname)        
            self.ax1.set_title('Spectral Typing '+self.srcname)
            self.ax1.axis((3850,4600,0,2.0))
            self.ax2.axis((3850,4600,0,1.2))
            plt.draw()

        if event.key == 'right':
            # Clear the plot
            self.ax.cla()
            self.ax1.cla()
            self.ax2.cla()
            # Higher luminosity class
            self.lumi = self.lumi + 1
            self.ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
            self.ax.grid(False)
            self.ax.set_xlabel(r'$\lambda$ ($\AA$)')
            self.ax.set_ylabel('Rectified Intensity + Offset')
            self.ax1.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax1.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax1.plot(self.wv,self.spec+0.4,'k-')
            self.ax1.text(4500,1.45,self.srcname)
            self.ax1.plot(self.goldstds[:,0,self.sp1i,self.lumi],self.goldstds[:,1,self.sp1i,self.lumi]+0.8,'r-')
            self.ax1.text(4500,1.85,self.goldsptypes[self.sp1i][self.lumi])
            self.ax2.plot(self.goldstds[:,0,self.sp2i,self.lumi],self.goldstds[:,1,self.sp2i,self.lumi],'r-')
            self.ax2.text(4500,0.8,self.goldsptypes[self.sp2i][self.lumi])
            self.ax2.plot(self.wv,self.spec,'k-')
            self.ax2.text(4500,1.05,self.srcname)        
            self.ax1.set_title('Spectral Typing '+self.srcname)
            self.ax1.axis((3850,4600,0,2.0))
            self.ax2.axis((3850,4600,0,1.2))
            plt.draw()


    # READGOLDS: Read in the gold standard spectra
    def readgolds(self):
        # The spectral types
        sptypes = [['O9V','O9IV','O9III','O9II','O9Iab'],
                   ['O9.5V','O9.5IV','O9.5III','O9.5II','O9.5Ib'],
                   ['B0V','B0IV','B0III','B0II','B0Ib'],
                   ['B0.5V','B0.5IV','B0.5III','B0.5II','B0.5I'],
                   ['B1V','B1IV','B1III','B1II','B1Ia'],
                   ['B1.5V','B1.5IV','B1.5III','B1.5II','B1.5Ia'],
                   ['B2V','B2IV','B2III','B2II','B2I'],
                   ['B2.5V','B2.5IV','B2.5III','B2.5II','B2.5I'],
                   ['B3V','B3IV','B3III','B3II','B3I'],
                   ['B5V','B5IV','B5III','B5II','B5I'],
                   ['B7V','B7IV','B7III','B7II','B7I'],
                   ['B8V','B8IV','B8III','B8II','B8I'],
                   ['B9V','B9IV','B9III','B9II','B9I'],
                   ['A0V','A0IV','A0III','A0II','A0I'],
                   ['A1V','A1IV','A1III','A1II','A1I'],
                   ['A3V','A3IV','A3III','A3II','A2I'],
                   ['A5V','A5IV','A5III','A5II','A5I'],
                   ['A7V','A7IV','A7III','A7II','A7I'],
                   ['A9V','A9IV','A9III','A9II','A9I']]
        # MKCLASS data directory:
        mkcdir = '/usr/local/mkclass/libr18/'
        # AO data directory:
        datadir = '/home/dwhelan/analysis/OBA_AO/data/'
        testsp = np.loadtxt(mkcdir+'t060l10p00.rbn')
        # golds: numwvs, (wvs,flx), # sp types, 5 lum classes (I,II,III,IV,V)
        golds = np.zeros((testsp.shape[0],2,len(sptypes),len(sptypes[0]))).copy()
        # O9 stars:
        golds[:,:,0,0] = np.loadtxt(datadir+'HD214680_20171009.txt',skiprows=409,usecols=(0,3))#mkcdir+'t060l50p00.rbn')
        golds[:,:,0,2] = np.loadtxt(datadir+'HD024431_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t060l30p00.rbn')
        golds[:,:,0,4] = np.loadtxt(datadir+'HD210809_20171014.txt',skiprows=409,usecols=(0,3))#mkcdir+'t060l10p00.rbn')
        # O9.5 stars:
        golds[:,:,1,0] = np.loadtxt(datadir+'HD034078_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,1,2] = np.loadtxt(datadir+'HD189957_20170910.txt',skiprows=409,usecols=(0,3))
        golds[:,:,1,4] = np.loadtxt(datadir+'HD209975_20171014.txt',skiprows=409,usecols=(0,3))
        # B0 stars:
        golds[:,:,2,0] = np.loadtxt(datadir+'HD036512_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t070l50p00.rbn')
        golds[:,:,2,2] = np.loadtxt(mkcdir+'t070l30p00.rbn')
        golds[:,:,2,4] = np.loadtxt(datadir+'HD164402_20170524.txt',skiprows=409,usecols=(0,3))#mkcdir+'t070l10p00.rbn')
        # B0.5
        golds[:,:,3,0] = np.loadtxt(datadir+'HD036960_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,3,1] = np.loadtxt(datadir+'HD034816_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,3,2] = np.loadtxt(datadir+'HD218376_20171013.txt',skiprows=409,usecols=(0,3))
        golds[:,:,3,4] = np.loadtxt(datadir+'HD038771_20180105.txt',skiprows=409,usecols=(0,3))
        # B1 stars:
        golds[:,:,4,0] = np.loadtxt(datadir+'HD144470_20170524.txt',skiprows=409,usecols=(0,3))#mkcdir+'t080l50p00.rbn')
        golds[:,:,4,2] = np.loadtxt(mkcdir+'t080l30p00.rbn')
        golds[:,:,4,4] = np.loadtxt(datadir+'HD013854_20171126.txt',skiprows=409,usecols=(0,3))#np.loadtxt(mkcdir+'t080l10p00.rbn')
        # B1.5 stars:
        golds[:,:,5,0] = np.loadtxt(datadir+'HD154445_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,5,2] = np.loadtxt(datadir+'HD214993_20171013.txt',skiprows=409,usecols=(0,3))
        # B2 stars:
        golds[:,:,6,0] = np.loadtxt(mkcdir+'t090l50p00.rbn')
        golds[:,:,6,1] = np.loadtxt(datadir+'HD000886_20171009.txt',skiprows=409,usecols=(0,3))
        golds[:,:,6,2] = np.loadtxt(datadir+'HD030836_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t090l30p00.rbn')
        golds[:,:,6,4] = np.loadtxt(datadir+'HD206165_20171009.txt',skiprows=409,usecols=(0,3))#mkcdir+'t090l10p00.rbn')
        # B2.5 stars:
        golds[:,:,7,0] = np.loadtxt(datadir+'HD148605_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,7,2] = np.loadtxt(datadir+'HD207330_20171009.txt',skiprows=409,usecols=(0,3))
        golds[:,:,7,4] = np.loadtxt(datadir+'HD198478_20170922.txt',skiprows=409,usecols=(0,3))
        # B3 stars:
        golds[:,:,8,0] = np.loadtxt(datadir+'HD020365_20171126.txt',skiprows=409,usecols=(0,3))#mkcdir+'t100l50p00.rbn')
        golds[:,:,8,1] = np.loadtxt(datadir+'HD037711_20180303.txt',skiprows=409,usecols=(0,3))
        golds[:,:,8,2] = np.loadtxt(datadir+'HD021483_20170109.txt',skiprows=409,usecols=(0,3))#mkcdir+'t100l30p00.rbn')
        golds[:,:,8,4] = np.loadtxt(mkcdir+'t100l10p00.rbn')
        # B5 stars:
        golds[:,:,9,0] = np.loadtxt(datadir+'HD034759_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t120l50p00.rbn')
        golds[:,:,9,1] = np.loadtxt(datadir+'HD147394_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,9,2] = np.loadtxt(datadir+'HD034503_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t120l30p00.rbn')
        golds[:,:,9,4] = np.loadtxt(datadir+'HD164353_20160630.txt',skiprows=409,usecols=(0,3))#mkcdir+'t120l10p00.rbn')
        # B7 stars:
        golds[:,:,10,0] = np.loadtxt(datadir+'HD021071_20170109.txt',skiprows=409,usecols=(0,3))#mkcdir+'t130l50p00.rbn')
        golds[:,:,10,1] = np.loadtxt(datadir+'HD028503B_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,10,2] = np.loadtxt(datadir+'HD035497_20171211.txt',skiprows=409,usecols=(0,3))#mkcdir+'t130l30p00.rbn')
        golds[:,:,10,4] = np.loadtxt(mkcdir+'t130l10p00.rbn')
        # B8 stars:
        golds[:,:,11,0] = np.loadtxt(datadir+'HD023324_20171126.txt',skiprows=409,usecols=(0,3))#mkcdir+'t140l50p00.rbn')
        golds[:,:,11,1] = np.loadtxt(datadir+'HD022203_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,11,2] = np.loadtxt(datadir+'HD023850_20171126.txt',skiprows=409,usecols=(0,3))#mkcdir+'t140l30p00.rbn')
        golds[:,:,11,4] = np.loadtxt(datadir+'HD208501_20171009.txt',skiprows=409,usecols=(0,3))#mkcdir+'t140l10p00.rbn')
        # B9 stars:
        golds[:,:,12,0] = np.loadtxt(datadir+'HD016046_20171126.txt',skiprows=409,usecols=(0,3))#mkcdir+'t150l50p00.rbn')
        golds[:,:,12,1] = np.loadtxt(datadir+'HD196867_20170910.txt',skiprows=409,usecols=(0,3))
        golds[:,:,12,2] = np.loadtxt(datadir+'HD176437_20170922.txt',skiprows=409,usecols=(0,3))#mkcdir+'t150l30p00.rbn')
        golds[:,:,12,3] = np.loadtxt(datadir+'HD178065_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,12,4] = np.loadtxt(datadir+'HD021291_20171126.txt',skiprows=409,usecols=(0,3))#mkcdir+'t150l10p00.rbn')
        # A0 stars:
        golds[:,:,13,0] = np.loadtxt(datadir+'HD172167_20170524.txt',skiprows=409,usecols=(0,3))#mkcdir+'t160l50p00.rbn')
        golds[:,:,13,1] = np.loadtxt(datadir+'HD210419_20171009.txt',skiprows=409,usecols=(0,3))
        golds[:,:,13,2] = np.loadtxt(datadir+'HD087887_20170524.txt',skiprows=409,usecols=(0,3))#mkcdir+'t160l30p00.rbn')
        golds[:,:,13,4] = np.loadtxt(datadir+'HD021389_20170109.txt',skiprows=409,usecols=(0,3))#mkcdir+'t160l10p00.rbn')
        # A1 stars:
        golds[:,:,14,0] = np.loadtxt(datadir+'HD009132_20171126.txt',skiprows=409,usecols=(0,3))#np.loadtxt(mkcdir+'t170l50p00.rbn')
        golds[:,:,14,1] = np.loadtxt(datadir+'HD216735_20171013.txt',skiprows=409,usecols=(0,3))
        golds[:,:,14,2] = np.loadtxt(mkcdir+'t170l30p00.rbn')
        golds[:,:,14,4] = np.loadtxt(mkcdir+'t170l10p00.rbn')
        # A2/3 stars:
        golds[:,:,15,0] = np.loadtxt(datadir+'HD102647_20170524.txt',skiprows=409,usecols=(0,3))#mkcdir+'t190l50p00.rbn')
        golds[:,:,15,1] = np.loadtxt(datadir+'HD033111_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,15,2] = np.loadtxt(mkcdir+'t190l30p00.rbn')
        golds[:,:,15,4] = np.loadtxt(datadir+'HD197345_20170910.txt',skiprows=409,usecols=(0,3))#mkcdir+'t190l10p00.rbn')
        # A5 stars:
        golds[:,:,16,0] = np.loadtxt(datadir+'HD023194_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,16,2] = np.loadtxt(mkcdir+'t200l30p00.rbn')
        golds[:,:,16,3] = np.loadtxt(datadir+'HD147084_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,16,4] = np.loadtxt(mkcdir+'t200l10p00.rbn')
        # A7 stars:
        golds[:,:,17,0] = np.loadtxt(datadir+'HD087696_20170524.txt',skiprows=409,usecols=(0,3))
        golds[:,:,17,1] = np.loadtxt(datadir+'HD076644_20180303.txt',skiprows=409,usecols=(0,3))
        golds[:,:,17,2] = np.loadtxt(datadir+'HD028319_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,17,4] = np.loadtxt(mkcdir+'t210l10p00.rbn')
        # A9 stars:
        golds[:,:,18,0] = np.loadtxt(datadir+'HD008511_20171211.txt',skiprows=409,usecols=(0,3))
        golds[:,:,18,2] = np.loadtxt(datadir+'HD147547_20170524.txt',skiprows=409,usecols=(0,3))
        return golds,sptypes
