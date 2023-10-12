import numpy as np

#hist = np.zeros(10000)

class Histogram:
    def __init__(self, size, max):
        self.hist = np.zeros(size)
        self.maximum = max
        self.bin = np.floor(max/size)
        self.size = size
    def addToHist(self, buffer):
        for value in buffer:
            ValIndex = int(np.floor(value/self.bin))
            if(ValIndex<self.maximum):
                self.hist[ValIndex] = self.hist[ValIndex] + 1
            else:
                self.hist[self.size-1] = self.hist[self.size-1] + 1
    def clearHist(self):
        self.hist = np.zeros(self.size)

GUI_hist = Histogram(1000,10000)