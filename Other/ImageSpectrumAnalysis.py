import numpy as np

class ImageSpectrumAnalysis:
    def getTotalSpectrum(img):
        dims = np.shape(img)
        spectLength = dims[2]

        spect = np.sum(np.sum(img, axis=0), axis=0)

        return spect
    
    def getPixelSpectrum(img, coordinates):
        return img[int(coordinates[0])][int(coordinates[1])][:]
    
    def getRowSpectrum(img, row):
        return np.sum(img[:,int(row),:], axis=0)
    
    def getColumnSpectrum(img, column):
        return np.sum(img[int(column),:,:], axis=0)