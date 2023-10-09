import os
import re

dir_path = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\Fragments_dirty"

#Bat file location
clus_script_location = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\Console_clustering\clustering_console.exe"

#Calibration file location
a = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\dummy_calibration\a.txt"
b = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\dummy_calibration\b.txt"
c = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\dummy_calibration\c.txt"
t = r"C:\Users\Urban\Documents\MATLAB\LosAlamos\Scripts\dummy_calibration\t.txt"

# iterate each file in a directory
for file in os.listdir(dir_path):
    cur_path = os.path.join(dir_path, file)
    # check if it is a file
    if os.path.isfile(cur_path):
        #Check if file name contains word trigger
        if( 'WindowedData' in file):
            #Apply the clustering
            clustering_call = clus_script_location + ' ' + cur_path + ' ' + a + ' ' + b + ' ' + c + ' ' + t + ' ' + "50e-9"
            os.system(clustering_call)
                        
