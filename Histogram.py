import numpy as np

##Basic histogram class
class Histogram:
    def __init__(self, size, max):
        self.hist = np.zeros(size)
        self.maximum = max
        self.bin = np.floor(max/size)
        self.size = size

    #Add buffered values to hte histogram
    def addToHist(self, buffer):
        for value in buffer:
            ValIndex = int(np.floor(value/self.bin))
            if(ValIndex<self.size):
                self.hist[ValIndex] = self.hist[ValIndex] + 1
            else:
                self.hist[self.size-1] = self.hist[self.size-1] + 1

    #Clear the histogram - set all bins to 0
    def clearHist(self):
        self.hist = np.zeros(self.size)

##Contains hit-counts for 3 channels
class HitCounts:
    def __init__(self):
        self.CH1 = 0
        self.CH2 = 0
        self.CH3 = 0
    def clearCounters(self):
        self.CH1 = 0
        self.CH2 = 0
        self.CH3 = 0
    def addCount(self, channel, value):
        if(channel == 1):
           self.CH1 = self.CH1 + value
        elif(channel == 2):
           self.CH2 = self.CH2 + value
        elif(channel == 3):
           self.CH3 = self.CH3 + value

##Global histogram class
GUI_hist = Histogram(1000,10000)

##Global hit counts - not neede in this version
#GUI_hitcnts = HitCounts()