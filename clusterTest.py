import cluster as Cl
import matplotlib.pyplot as plt

myTestCluster = Cl.Cluster([[256*100+100,20],[256*100+355,10],[256*100+101,15]], [256*100+101,256*100+101], 3)

img = myTestCluster.drawCluster()
imgplot = plt.imshow(img, cmap='hot', aspect='auto')
plt.show()
