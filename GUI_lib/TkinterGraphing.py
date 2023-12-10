import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
     FigureCanvasTkAgg)
import tkinter as tk
import customtkinter
import numpy as np

class Tkinter_Graphing:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots()
        # Tkinter Application
        self.frame = tk.Frame(master)
        self.frame.pack(fill='none', expand=0)# fill='both', expand=1)

        # Create Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master)  
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=0)#fill=tk.BOTH, expand=1)
        

        #self.navBar = tk.NavigationToolbar2Tk(self.canvas, master)
        #self.navBar.pack(side = tk.TOP, expand=1)
    def addColorBar(self, Im):
        self.cb = self.fig.colorbar(Im)#colorbar(Im)

    def show_image(self, img):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        #self.ax.clear()
        #plt.cla()
        #if(self.fig.axes.__len__()>1):
        #    self.cb.remove()
        Im = self.ax.imshow(img)
        self.addColorBar(Im)
        self.canvas.draw()

    def show_plot(self, x,y):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        #self.ax.clear()
        #plt.cla()
        #if(self.fig.axes.__len__()>1):
        #    self.cb.remove()
        #self.ax.clear()
        Im = self.ax.plot(x, y )
        
        self.canvas.draw()

    def show_hist(self, x):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        #self.ax.clear()
        #plt.cla()
        #if(self.fig.axes.__len__()>1):
        #    self.cb.remove()
        #self.ax.clear()
        Im = self.ax.hist(x, bins=2000, color='b')
        
        self.canvas.draw()

    def show_bar(self, x, y):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        
        Im = self.ax.bar(x, y )
        
        self.canvas.draw()
