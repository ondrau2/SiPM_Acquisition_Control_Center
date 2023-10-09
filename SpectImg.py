import numpy as np


def getSpectralImage(img, ranges):
    E_IMG = np.zeros(np.shape(img[:,:,1]))

    for range in ranges:
        E_IMG = np.add(E_IMG, np.sum(img[:,:,int(range[0]):int(range[1])], axis = 2 ))
    return E_IMG