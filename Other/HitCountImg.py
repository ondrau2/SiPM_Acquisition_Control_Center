import numpy as np

def getHitCountImage(histograms):
    return np.sum(histograms.hist, 2)
