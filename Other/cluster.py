import numpy as np
import matplotlib.pyplot as plt

class Cluster:
    def __init__(self, PxRaw, centroid_xy, size):
        self.PxRaw = PxRaw
        self.centroid_xy = centroid_xy
        self.size = size
    def drawCluster(self):
        img = [ [0]*256 for i in range(256)]
        for px in range(0, self.size):
            x = int(np.floor(self.PxRaw[px][0]/256))
            y = int(self.PxRaw[px][0]%256)
            img[x][y] = self.PxRaw[int(px)][1]
        return img
    