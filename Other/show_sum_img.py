import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pickle
import histogramCreation
import os

# Load the stored data
with open(r"hist_t1.pickle", "rb") as input_file:
   histograms = pickle.load(input_file)
   hist_sum = np.sum(histograms.hist, 2)

# Show the image
plt.imshow(hist_sum, interpolation='none', cmap='hot')
plt.colorbar()
plt.show()

print('Done')