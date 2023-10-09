import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pickle
import histogramCreation
import os

selected_pixel_coordinates = [128,255]

# Load the stored data
with open(r"hitRate_hist_t1.pickle", "rb") as input_file:
   hitRate_histograms = pickle.load(input_file)
   selPxHitRate = hitRate_histograms.timeHist[selected_pixel_coordinates[0]][selected_pixel_coordinates[1]][:]

totalhitRate_0 = np.sum(hitRate_histograms.timeHist,0)
totalhitRate = np.sum(totalhitRate_0,0)

#Get the max-min hitrate difference
hitRate_diff = np.amax(hitRate_histograms.timeHist, 2) - np.amin(hitRate_histograms.timeHist, 2)

# Show the images
x = np.linspace(0, len(selPxHitRate), len(selPxHitRate))
y = selPxHitRate

plt.figure(0)
plt.subplot(2,1,1)

plt.stem(x, y)
plt.xlabel('Time [s]')
plt.ylabel('Hits [-]')
plt.title('Hits for selected pixel')

plt.subplot(2,1,2)
plt.stem(x, totalhitRate)
plt.xlabel('Time [s]')
plt.ylabel('Hits [-]')
plt.title('Total hit rate')

plt.tight_layout()
plt.show()

plt.figure(1)
plt.imshow(hitRate_diff, interpolation='none', cmap='hot')
plt.colorbar()
plt.show()

print('Done')