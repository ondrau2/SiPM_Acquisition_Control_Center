import os
import numpy
import matplotlib.pyplot as plt
import numpy as np
import cluster as clus
import re
import pickle as pickle

global hist
global timeHist
global histogram_matrix
global histograms

def getProcessedData(clusteredFilePath, outputFilePath):
    # Path to the clustered .txt file
    px_clusters_path = clusteredFilePath #r"Z:\measurement\XRD\Fan_beam\Elements_calibration\Copper\res\I5_close_px.txt"
    timeStep_s = 0.2
    time_max_s= 0.2*20
    energy_max = 100

    #Decide whether use single pixel clusters or all clusters
    singlePixelClustersOnly = True


    class histogram_matrix:
        def __init__(self, x_size, y_size, bin_num, timeStep, maxTime):
            
            self.hist = np.empty([x_size, y_size, bin_num]) 
            self.timeHist = np.empty([x_size, y_size, int(np.ceil(maxTime/timeStep))])
            
        def addEventToHistogram(self, coordinates, energy):
            egy = int(np.floor(energy))
            if(egy<energy_max):
                self.hist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [egy] = self.hist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [egy] + 1
        def addEventToHitRateHistogram(self, coordinates, ToA):
            ToA_recalc = ToA*1e-9
            if(ToA_recalc < time_max_s):
                self.timeHist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [int(np.floor(ToA_recalc/timeStep_s))] = self.timeHist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [int(np.floor(ToA_recalc/timeStep_s))] + 1
        def saveData(self):
            with open(outputFilePath, "wb") as output_file:
                pickle.dump(self, output_file)

    class hitRate_histogram:
        def __init__(self, x_size, y_size, timeStep, maxTime):
            self.timeHist = np.empty([x_size, y_size, int(np.ceil(maxTime/timeStep))])
        def addEventToHitRateHistogram(self, coordinates, ToA):
            ToA_recalc = ToA*1e-9
            if(ToA_recalc < time_max_s):
                self.timeHist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [int(np.floor(ToA_recalc/timeStep_s))] = self.timeHist[int(np.floor(coordinates[0]))] [int(np.floor(coordinates[1]))] [int(np.floor(ToA_recalc/timeStep_s))] + 1


    # Init the variables
    histograms = histogram_matrix(256, 256, energy_max, timeStep_s, time_max_s)
    #hitRate_hist = hitRate_histogram(256,256, timeStep_s, time_max_s)
    centroid_x = 0
    centroid_y = 0
    px_cnt = 0
    tot_energy = 0
    first_ToA = np.inf

    with open(px_clusters_path) as file:
        for line in file:
            # Do something...
            if("#" in line):
                # Got the full cluster
                if(tot_energy>0):
                    centroid_x = centroid_x/tot_energy
                    centroid_y = centroid_y/tot_energy            
                    histograms.addEventToHistogram([centroid_x, centroid_y], tot_energy)
                    histograms.addEventToHitRateHistogram([centroid_x, centroid_y], first_ToA)

                # Null the variables
                centroid_x = 0
                centroid_y = 0
                px_cnt = 0
                tot_energy = 0
                first_ToA = np.inf
            else:
                # Add event to cluster
                lineData = re.findall(r'[-+]?(?:\d*\.*\d+)', str(line))
                if(np.size(lineData)>3):
                    px_cnt = px_cnt+1
                    px_egy = float(lineData[3])
                    centroid_x = centroid_x + int(lineData[0])*px_egy
                    centroid_y = centroid_y + int(lineData[1])*px_egy
                    tot_energy = tot_energy + px_egy
                    ToA = float(lineData[2])
                    if(ToA < first_ToA):
                        first_ToA = ToA

    histograms.saveData()

    return histograms

    #print('Done')

   # histograms.saveData()

    #histFilePath = outputFilePath + "_hist"
    #hitrateFilePath = outputFilePath + "_hitRate"
    


    #with open(hitrateFilePath, "wb") as output_file:
    #    pickle.dump(hitRate_hist, output_file)