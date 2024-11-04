import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
     FigureCanvasTkAgg)
import tkinter as tk
import customtkinter
import numpy as np
from CTkSpinbox import *

##Tkinter gui class for matplotlib
class Tkinter_Graphing:
    def __init__(self, master):
        self.xMax = customtkinter.IntVar(value  = 2000)
        self.binAdjust = customtkinter.IntVar(value  = 1)
        self.fig, self.ax = plt.subplots()
        # Tkinter Application
        self.frame = tk.Frame(master)
        self.frame.pack(fill='none', expand=0)# fill='both', expand=1)

        # Create Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master)  
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=0)#fill=tk.BOTH, expand=1)

        #Spinbox
        self.xlimitFrame = customtkinter.CTkFrame(master)
        self.xlimitFrame.pack(side=tk.TOP, fill='none', expand=tk.TRUE)# fill='both', expand=1)
        self.lbl_x_max = customtkinter.CTkLabel(self.xlimitFrame,text='X-limit: ')
        self.lbl_x_max.pack(side=tk.LEFT, fill=tk.NONE, expand=True)
        self.xMaxSpinbox = CTkSpinbox(self.xlimitFrame, start_value = 2000, min_value = 1, max_value = 2000,scroll_value = 50, step_value = 1, width = 300, variable = self.xMax)
        self.xMaxSpinbox.pack(side=tk.LEFT, fill=tk.NONE, expand=True)

        self.binFrame = customtkinter.CTkFrame(master)
        self.binFrame.pack(side=tk.TOP, fill='none', expand=tk.TRUE)# fill='both', expand=1)
        self.lbl_x_max = customtkinter.CTkLabel(self.binFrame,text='Bin adjust: ')
        self.lbl_x_max.pack(side=tk.LEFT, fill=tk.NONE, expand=True)
        self.xMaxSpinbox = CTkSpinbox(self.binFrame, start_value = 1, min_value = 1, max_value = 50,scroll_value = 1, step_value = 1, width = 300, variable = self.binAdjust)
        self.xMaxSpinbox.pack(side=tk.LEFT, fill=tk.NONE, expand=True)
        
    #Add the colorbar
    def addColorBar(self, Im):
        self.cb = self.fig.colorbar(Im)#colorbar(Im)

    #Show image function
    def show_image(self, img):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        Im = self.ax.imshow(img)
        self.addColorBar(Im)
        self.canvas.draw()

    #Basic plot show
    def show_plot(self, x,y):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
       
        #Eventually adjust binning
        if(self.binAdjust.get() != 1):
            i = 0
            x_i = x*self.binAdjust.get()
            y_i = np.zeros(int(np.size(x)))
            for value in y:
                #assuming sorted array
                if(value<self.binAdjust.get()*i):  
                   y_i[i] = y_i[i] + value
                   x_i[i] = i*self.binAdjust.get()
                else:
                   i =  i + 1

            Im = self.ax.plot(x_i, y_i)
        else: 
            Im = self.ax.plot(x, y)

        plt.xlim(0, self.xMax.get())
        
        self.canvas.draw()

    #Histogram show function
    def show_hist(self, x):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        
        Im = self.ax.hist(x, bins=2000, range = [0,500], color='b')
        
        self.canvas.draw()

    #Show bar graph
    def show_bar(self, x, y):
        #clear
        self.fig.clear()
        self.ax = self.fig.add_axes([0.1,0.1,0.8,0.8])
        
        Im = self.ax.bar(x, y )
        
        self.canvas.draw()

    def updateLimits(self, lim):
        self.plt.xlim(0, lim)
    
