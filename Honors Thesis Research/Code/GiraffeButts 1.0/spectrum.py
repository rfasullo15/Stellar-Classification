'''
The purpose of a spectrum object is to maintain the calculated values for a given spectrum.

History:

6/25/2018: Class created. Spectrum objects can calculate the location of their H absorption lines

7/2/2018: isRectified, calWaves, and recWaves added.

@rfasullo

'''
import numpy as np
import copy

class Spectrum:

    def __init__(self, name):

        self.namaste = name

        self.wv = []                      # calibrated wavelengths
        self.raw = []                    # raw 
        self.rms = []                    # raw minus sky
        self.rectified = []           # rectified spectrum
        self.waves = []                # wavelengths
        self.snr = []                    #  signal to noise ratio

        '''
        self.avg = 0
        '''
        #Info related to wave calibration
        '''
        self.keys = None
        self.values = [0,0,0]
        self.grpsize = 8
        self.peaks = []
        self.origpeaks = []
        self.isSolved = False

        '''
        #Info related to continuum rectification
        '''
        self.isRectified = False

        '''
        #Info related to spectral typing
        '''
        self.spectype = ""
        self.isTyped = False
        '''

    def setVals(self, wv, raw, rms, rectified, waves, snr):
        self.wv = wv
        self.raw = raw
        self.rectified = rectified
        self.waves = waves
        self.snr = snr

    def __repr__(self):
        return ("Spectrum for " + self.namaste)

    '''    
    def setKeys(self, keys):
        self.keys = keys
        self.peaks = self.findpeaks()
        self.origpeaks = copy.deepcopy(self.peaks)

    def setRMS(self, rms):
        self.rms = rms
        self.avg = sum(self.rms)/len(self.rms)
        

    def findpeaks(self):
        if self.keys ==None:
            print("No Keys")
            start = 0
            finish = start + self.grpsize
            peakindex = []
            
            while finish < 2048:
                section = np.array(self.waves[start:finish])
                downcheck = -np.sort(-section)
                upcheck = np.sort(section)
                if np.array_equal(section, downcheck):
                    val, index = self.recurse_down(finish)
                    peakindex.append([val,index,start, start + 2*(index-start)])
                    print(peakindex)
                    finish = index
                elif np.array_equal(section, downcheck):
                    val, index = self.recurse_up(finish)
                    peakindex.append((val,index))
                    finish = index

                start = finish
                finish = start + self.grpsize

             
            peaks = []
            for pk in peakindex:
                rwing = self.waves[pk[2]]
                if pk[3] >2047:
                    pk[3] = 2047
                lwing = self.waves [pk[3]]
                peak = pk[0]
                localcont = rwing # approx. height of the "top" of the absorption/emission line

                if np.absolute(rwing - peak) > 12000 or np.absolute(lwing - peak) > 12000:
                    peaks.append(pk)
                    
            peaks = self.pickpeak([elem[1] for elem in peaks])
            print(peaks)

            return peaks
        else:
            print("Keys")
            start = 0
            finish = start +self.grpsize
            firstpeak = -1

            while finish <2048:
                section = np.array(self.waves[start:finish])
                downcheck = -np.sort(-section)
                depthcheck = np.absolute(downcheck[0] - downcheck[len(downcheck) - 1])
                if depthcheck > 3000:
                    val, index = self.recurse_down(finish)
                    firstpeak = [val,index,start, start + 2*(index-start)]
                    rwing = self.waves[firstpeak[2]]
                    lwing = self.waves [firstpeak[3]]
                    peak = firstpeak[0]
                    localcont = rwing # approx. height of the "top" of the absorption/emission line
                    rdep = rwing - peak
                    ldep = lwing - peak
                    if rdep > 11000 or ldep > 11000:
                        break
                '''
    '''
                elif depthcheck > 1000 and np.array_equal(section, upcheck):
                    val, index = self.recurse_up(finish)
                    downside = np.array(self.waves[index: index + self.grpsize])
                    downcheck = -np.sort(-downside)
                    if np.array_equal(downside, downcheck):
                        print("Poops")
                        firstpeak = [val,index,start, start + 2*(index-start)]
                        print(firstpeak)
                        rwing = self.waves[firstpeak[2]]
                        lwing = self.waves [firstpeak[3]]
                        peak = firstpeak[0]
                        localcont = rwing # approx. height of the "top" of the absorption/emission line
                        rdep = rwing - peak
                        ldep = lwing - peak
                        if rdep > 12000 or ldep > 12000:
                            break
                
                start = finish
                finish = start+self.grpsize
                
            peaks = []       
            if firstpeak == -1:
                return [0,0,0,0,0,0]
            else:
                peaks.append(firstpeak[1])
                count = 0
                while count<len(self.keys):
                    if self.keys[count] + peaks[count] <= 2047:
                        peaks.append(self.keys[count] + peaks[count])
                        count +=1
                    else:
                        break
            #if len(set(peaks)) < 6:
               # return [0,0,0,0,0,0]

            peaks = self.pickpeak(peaks)
            return peaks
                                                             
    def recurse_down(self, index):
        val, idx = self.fall_down(index)
        tempsect = np.array(self.waves[idx:(idx+self.grpsize)])
        count = 0
        tempidx = idx
        while count<len(tempsect):
            if tempsect[count] < val:
                val,idx = self.recurse_down(tempidx)
                break
            count +=1
            tempidx +=1
        return (val, idx)
    
    def recurse_up(self, index):
        val, idx = self.climb_up(index)
        tempsect = np.array(self.waves[idx:(idx+self.grpsize)])
        count = 0
        tempidx = idx
        while count< len(tempsect):
            if tempsect[count] > val:
                val,idx = self.recurse_up(tempidx)
                break
            count +=1
            tempidx +=1
        return (val,idx)


    def pickpeak(self, wantedindeces):
        
        peaks = []
        buffer = 5
        for index in wantedindeces:
            templist = self.waves[int(index-buffer) : int(index+buffer)]
            #if self.waves[index] > self.avg:
             #       templist = -np.sort(-templist)
            #else:
            templist = np.sort(templist)
            if len(np.nonzero(self.waves == templist[0])[0]) == 1:
                peaks.append(np.nonzero(self.waves == templist[0])[0][0])
            else:
                multiples = np.nonzero(self.waves == templist[0])
                for idx in multiples[0]:
                    if idx < index+buffer and idx > index-buffer:
                        peaks.append(idx)
        return peaks
    
    '''
    #Travels down a negative slope until it reaches the end
    '''
    def fall_down(self, start):
        if start < 2047:
            curr = self.waves[start]
            nxt = self.waves[start+1]
            count = start+1

            while curr>nxt and count < 2047:
                curr = nxt
                count+=1
                nxt = self.waves[count]

            return (curr, count)
        else:
            return (self.waves[start], start)

    '''
    #Travels up a positive slope until it reaches the peak
    '''
    def climb_up(self, start):
        if start < 2046:
            curr = self.waves[start]
            nxt = self.waves[start+1]
            count = start + 1

            while curr<nxt:
                curr = nxt
                count +=1
                nxt = self.waves[count]

            return (curr, count)
        else:
            return (self.waves[start], start)

    def gen_keys(self):
        self.peaks = self.findpeaks()
        keys = [self.peaks[0]]

        count = 0

        while count < len(self.peaks) - 1:
                keys.append(self.peaks[count + 1] - self.peaks[count])
                count +=1

        return keys
                                

    def resetpeaks(self):
        self.peaks  = copy.deepcopy(self.origpeaks)
        
    def removepeak(self, pek):
        buffer = 5
        lowerpek = int(pek) - 5
        upperpek = int(pek) + 5
        toremove=None
        for p in self.peaks:
            if p > lowerpek and p < upperpek:
                toremove = p

        self.peaks.remove(p)
        
    def addpeak(self, pek):
        self.peaks.append(self.pickpeak([pek])[0])

    '''
    
        
    
                
        


