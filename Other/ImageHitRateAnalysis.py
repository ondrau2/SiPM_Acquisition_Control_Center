import numpy as np

class ImageHitRateAnalysis:
    def getTotalSpectrum(hitrateHist, timeStep):
        dims = np.shape(hitrateHist)
        spectLength = dims[2]

        spect = np.sum(np.sum(hitrateHist, axis=0), axis=0)
        t = np.linspace(0, np.ceil(timeStep*spectLength), spectLength)

        return [t,spect]
    
    def getPixelSpectrum(hitrateHist, coordinates, timeStep):
        dims = np.shape(hitrateHist)
        spectLength = dims[2]

        spect = hitrateHist[int(coordinates[0])][int(coordinates[1])][:]
        t = np.linspace(0, np.ceil(timeStep*spectLength), spectLength)

        return [t,spect]
    
    def getRowSpectrum(hitrateHist, row, timeStep):
        dims = np.shape(hitrateHist)
        spectLength = dims[2]

        spect = np.sum(hitrateHist[:,int(row),:], axis=0)
        t = np.linspace(0, np.ceil(timeStep*spectLength), spectLength)

        return [t,spect]
    
    def getColumnSpectrum(hitrateHist, column, timeStep):
        dims = np.shape(hitrateHist)
        spectLength = dims[2]

        spect = np.sum(hitrateHist[int(column),:,:], axis=0)
        t = np.linspace(0, np.ceil(timeStep*spectLength), spectLength)

        return [t,spect]