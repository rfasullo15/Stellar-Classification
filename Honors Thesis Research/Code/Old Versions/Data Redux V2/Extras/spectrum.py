'''
The purpose of a spectrum object is to maintain the calculated values for a given spectrum.

History:

6/25/2018: Class created

'''
import numpy as np

class Spectrum:

	def __init__(self, waves, name):

		self.waves = waves
		self.name = name
		self.isSolved = False
		self.values = [0,0,0]
		self.grpsize = 8
		self.peaks = self.findpeaks()
		

	def findpeaks(self):
		start = 0
		finish = start + self.grpsize
		peakindex = []
		pstart = 0


		while finish < 2048:
			section = np.array(self.waves[start:finish])
			downcheck = -np.sort(-section)
			if np.array_equal(section, downcheck):
				pstart = section[0]
				val, index = self.recurse_search(finish)
				peakindex.append((val,index))
				finish = index

			start = finish
			finish = start + self.grpsize

	def pickpeak(self, wantedindeces):
		peaks = []
		buffer = 4
		for index in wantedindeces:
			templist = self.waves[index-buffer : index+buffer]
			templist = np.sort(templist)
			if len(np.nonzero(self.waves == templist[0])[0]) == 1:
				peaks.append(np.nonzero(self.waves == templist[0])[0][0])
			else:
				multiples = np.nonzero(self.waves == templist[0])
				for idx in multiples[0]:
					if idx < index+buffer and idx > index-buffer:
						peaks.append(idx)
		return peaks	

	def recurse_search(self, index):
		val, idx = self.fall_down(index)
		tempsect = np.array(self.waves[idx:(idx+self.grpsize)])
		count = 0
		tempidx = idx
		while count<tempsect.__len__():
			if tempsect[count] < val:
				val,idx = self.recurse_search(tempidx)
				break
			count +=1
			tempidx +=1
		return (val, idx)

	def fall_down(self, start):
		curr = self.waves[start]
		next = self.waves[start+1]
		count = start+1

		while curr>next:
			curr = next
			count+=1
			next = self.waves[count]

		return (curr, count)

				
		


