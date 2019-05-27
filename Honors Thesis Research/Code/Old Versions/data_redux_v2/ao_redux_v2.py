#/usr/bin/python

# Import:

import spexredux as spx
import matplotlib.pyplot as plt
import numpy as np
import spec_type as st



#----------INITIAL PARAMETERS----------

# Data directory
datadir = './2018-04-10/'

# image files and names
imfiles = ['ao-001.fit','ao-002.fit','ao-003.fit','ao-004.fit','ao-005.fit',
           'ao-006.fit','ao-007.fit','ao-008.fit','ao-009.fit','ao-010.fit',
           'ao-011.fit','ao-012.fit','ao-013.fit','ao-014.fit','ao-015.fit',
           'ao-016.fit']
srcnames= ['HD47105','HD51638','HD52559','HD55579','HD56386',
           'HD56169','HD63021','HD68194','HD71072','HD69686',
           'HD71554','HD74217','HD75357','HD105262','HD109995',
           'HD98664']
lamp    = ['ao-017.fit']
flat    = ['ao-018.fit','ao-019.fit','ao-020.fit','ao-021.fit','ao-022.fit',
           'ao-023.fit','ao-024.fit','ao-025.fit','ao-026.fit','ao-027.fit',
           'ao-028.fit']
bias    = ['ao-029.fit','ao-030.fit','ao-031.fit','ao-032.fit','ao-033.fit',
           'ao-034.fit','ao-035.fit','ao-036.fit','ao-037.fit','ao-038.fit',
           'ao-039.fit','ao-040.fit','ao-041.fit','ao-042.fit','ao-043.fit',
           'ao-044.fit','ao-045.fit','ao-046.fit','ao-047.fit','ao-048.fit',
           'ao-049.fit','ao-050.fit','ao-051.fit','ao-052.fit','ao-053.fit']
alldarks= [['dark-001-120s.fit','dark-002-120s.fit','dark-003-120s.fit',
            'dark-004-120s.fit','dark-005-120s.fit','dark-006-120s.fit',
            'dark-007-120s.fit','dark-008-120s.fit','dark-009-120s.fit',
            'dark-010-120s.fit','dark-011-120s.fit','dark-012-120s.fit',
            'dark-013-120s.fit','dark-014-120s.fit','dark-015-120s.fit'],
           ['dark-001-300s.fit','dark-002-300s.fit','dark-003-300s.fit',
            'dark-004-300s.fit','dark-005-300s.fit','dark-006-300s.fit',
            'dark-007-300s.fit','dark-008-300s.fit','dark-009-300s.fit',
            'dark-010-300s.fit','dark-011-300s.fit','dark-012-300s.fit',
            'dark-013-300s.fit','dark-014-300s.fit','dark-015-300s.fit'],
           ['dark-001-600s.fit','dark-002-600s.fit','dark-003-600s.fit',
            'dark-004-600s.fit','dark-005-600s.fit','dark-006-600s.fit',
            'dark-007-600s.fit','dark-008-600s.fit','dark-009-600s.fit',
            'dark-010-600s.fit','dark-011-600s.fit','dark-012-600s.fit',
            'dark-013-600s.fit','dark-014-600s.fit','dark-015-600s.fit'],
           ['dark-001-1200s.fit','dark-002-1200s.fit','dark-003-1200s.fit',
            'dark-004-1200s.fit','dark-005-1200s.fit','dark-006-1200s.fit',
            'dark-007-1200s.fit','dark-008-1200s.fit','dark-009-1200s.fit',
            'dark-010-1200s.fit','dark-011-1200s.fit','dark-012-1200s.fit',
            'dark-013-1200s.fit','dark-014-1200s.fit','dark-015-1200s.fit']]
darkexptimes = [120.,300.,600.,1200.]

# Lines used in wavelength calibration:
#      H I   H I   H I   H I   H I
wvs = [4861.,4341.,4102.,3970.,3889.]

#----------END INITIAL PARAMETERS----------

#----------SOURCE EXTRACTION----------

finalspex = spx.extract(datadir,srcnames,imfiles,bias,flat,alldarks,
                        darkexptimes,wvfiles=lamp)

#----------END SOURCE EXTRACTION----------

#----------PLOT------------------------

test = np.loadtxt(srcnames[0]+'.txt',skiprows=1)
finalspex = np.zeros((test.shape[0],test.shape[1],len(srcnames))).copy()
for i in range(len(srcnames)):
    finalspex[:,:,i] = np.loadtxt(srcnames[i]+'.txt',skiprows=1)

for i in range(len(srcnames)):
    st.sptype(finalspex[:,0,i],finalspex[:,3,i],srcnames[i])

#----------END PLOT--------------------


