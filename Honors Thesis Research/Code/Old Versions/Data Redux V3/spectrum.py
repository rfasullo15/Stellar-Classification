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

    def __init__(self, waves, name, keys = None):

        self.waves = waves
        self.name = name
        self.isSolved = False
        self.values = [0,0,0]
        self.grpsize = 8
        self.peaks = self.findpeaks(keys)
        self.origpeaks = copy.deepcopy(self.peaks)
        
        

        self.isRectified = False
        self.calWaves = []
        self.recWaves = []
        


    def findpeaks(self, keys):

        if keys == None:
            start = 0
            finish = start + self.grpsize
            peakindex = []
            pstarts = []


            while finish < 2048:
                section = np.array(self.waves[start:finish])
                downcheck = -np.sort(-section)
                upcheck = np.sort(section)
                if np.array_equal(section, downcheck):
                    pstarts.append(section[0])
                    val, index = self.recurse_down(finish)
                    peakindex.append((val,index))
                    finish = index
                '''
                elif np.array_equal(section, upcheck):
                    pstarts.append(section[0])
                    val, index = self.recurse_up(finish)
                    peakindex.append((val,index))
                    finish = index
                '''
                
                start = finish
                finish = start + self.grpsize



            peakindex = list(set(peakindex)) #possibly extraneous
            #print(pstarts)
            wantedindeces = [elem[1] for elem in peakindex]
            peaks = self.pickpeak(wantedindeces, False)
            peaks = np.sort(peaks)
                                
            return peaks
        else:
            start = 0
            finish = start +self.grpsize
            firstpeak = -1

            while finish <2048:
                section = np.array(self.waves[start:finish])
                downcheck = -np.sort(-section)
                upcheck = np.sort(section)
                if np.array_equal(section, downcheck):
                    val, index = self.recurse_down(finish)
                    firstpeak = (val,index)
                    break
                '''
                elif np.array_equal(section, upcheck):
                    section = np.array(self.waves[start:finish])
                    val, index = self.recurse_up(finish)
                    firstpeak = (val, index)
                '''
                    
                start = finish
                finish = start+self.grpsize


            peaks = []
            peaks.append(firstpeak[1])

            count = 0
            while count<len(keys):
                peaks.append(keys[count] + peaks[count])
                count +=1

            peaks = self.pickpeak(peaks, False)

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


    def pickpeak(self, wantedindeces, isPeak):
        peaks = []
        buffer = 4
        for index in wantedindeces:
            templist = self.waves[int(index-buffer) : int(index+buffer)]
            if isPeak :
                    templist = -np.sort(-templist)
            else:
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
    Travels down a negative slope until it reaches the end
    '''
    def fall_down(self, start):
        curr = self.waves[start]
        nxt = self.waves[start+1]
        count = start+1

        while curr>nxt:
            curr = nxt
            count+=1
            nxt = self.waves[count]

        return (curr, count)

    '''
    Travels up a positive slope until it reaches the peak
    '''
    def climb_up(self, start):
        curr = self.waves[start]
        nxt = self.waves[start+1]
        count = start + 1

        while curr<nxt:
            curr = nxt
            count +=1
            nxt = self.waves[count]

    def gen_keys(self):
        keys = []

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
        avg = np.mean(np.array(self.waves))
        if self.waves[pek] > avg:
                self.peaks.append(self.pickpeak([pek], isPeak = True)[0])
        else:
                self.peaks.append(self.pickpeak([pek], isPeak = False)[0])
                
        


