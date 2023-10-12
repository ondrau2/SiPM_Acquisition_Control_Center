from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
from floatSpinBox import *
from PIL import ImageTk,Image
import matplotlib
import matplotlib.pyplot as plt
from tkinter import ttk
from ClusteredFileProcessing_v2 import *
from HitCountImg import *
from SpectImg import *
from TkinterGraphing import *
from ImageSpectrumAnalysis import *
from ImageHitRateAnalysis import *
from STM_serial import *
from Histogram import *

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
root = customtkinter.CTk()

###############################################################################
#################################----VARIABLES-----############################
global processedData

#Clustering params
timeStep_s = 0.2
time_max_s= 0.2*20
energy_max = 100


#analysisFrame = customtkinter.CTkFrame(root)
#analysisFrame.pack(side=BOTTOM, fill="both", expand=True)

RightPannelFrame = customtkinter.CTkFrame(root)
RightPannelFrame.pack(side=RIGHT, fill=BOTH, expand=True)

ConnectionPannel_Frame = customtkinter.CTkFrame(RightPannelFrame)
ConnectionPannel_Frame.pack(side=TOP, fill=BOTH)#, expand=True)

ImageFrame = customtkinter.CTkFrame(RightPannelFrame)
ImageFrame.pack(side=TOP, expand=False)

HistogramFrame = customtkinter.CTkFrame(ImageFrame)
HistogramFrame.pack(side=TOP, fill=None, expand=False)

#HitRateFrame = customtkinter.CTkFrame(ImageFrame)
#HitRateFrame.pack(side=TOP, expand=True, fill = BOTH)

# Create a graphing object
TKG = Tkinter_Graphing(HistogramFrame)
#TKG_HRC = Tkinter_Graphing(HitRateFrame)

#Fill with dummy data - make it show some default stuff
#arr = np.zeros((4,4))
#arr[1,2] = 1
#arr[0,3] = 2
#Tkinter_Graphing.show_image(TKG, arr)

#Serial
communication = STM_serial(115200)
communication.COM_connect("COM5")
gui_queue = Queue()
STM_serial.COM_Receive_Start(communication,gui_queue)

################################################################################################
###############################-----CONNECTION PANEL-----#######################################
class ConnectionPannelContents:
    def __init__(self, master):
        #Variables
        self.COM_NAME = StringVar()
        self.lbl_COM_name = customtkinter.CTkLabel(master,text='Select the COM port: ')
        self.lbl_COM_name.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM = customtkinter.CTkComboBox(master, variable=self.COM_NAME, command= self.COM_changed)
        self.cb_selCOM.configure(values = ["dummy1", "dummy2", "dummy3", "dummy4"])
        self.cb_selCOM.configure(state = 'readonly')
        self.cb_selCOM.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM.bind('<<ComboBoxSelected>>', self.COM_changed)

        self.btn_Connect = customtkinter.CTkButton(master, text="Connect", command=self.Connect_click)
        self.btn_Connect.pack(side=LEFT, fill=BOTH)
        
        self.lbl_device_state = customtkinter.CTkLabel(master,text='Device state')
        self.lbl_device_state.pack(side=RIGHT, fill=BOTH)

    def Connect_click(self):
        pass

    def COM_changed(self):
        pass
    



################################################################################################
###############################-----CONTROL PANEL-----##########################################
CtrlFrame = customtkinter.CTkFrame(root)
CtrlFrame.pack(side=LEFT, fill=BOTH, expand=1)

class AcquisitionSetup:
    def __init__(self, master):
        #Variables
        self.clusteredFilePath = ""
        #UI
        self.lbl_SelClusFile = customtkinter.CTkLabel(master,text='Select measurement file name:')
        self.lbl_SelClusFile.pack(side=TOP, fill=BOTH, pady=(30,0))
        selFileFrame = customtkinter.CTkFrame(master)
        selFileFrame.pack(side=TOP)
        self.tb_ClusFilePath = customtkinter.CTkEntry(selFileFrame, state="disabled")
        self.tb_ClusFilePath.pack(side=LEFT, fill=BOTH)
        self.btn_sel_clusFile = customtkinter.CTkButton(selFileFrame, text="Select", command=self.SelectFile_click)
        self.btn_sel_clusFile.pack(side=LEFT, fill=BOTH)

        self.NF_period = IntVar()
        self.Comp_lvl = DoubleVar()
        filePeriodSpecFrame = customtkinter.CTkFrame(master)
        filePeriodSpecFrame.pack(side=TOP, fill=BOTH)
        self.lbl_paramsSel = customtkinter.CTkLabel(filePeriodSpecFrame, text="New file period: ")
        self.lbl_paramsSel.pack(side=LEFT, fill=BOTH)
        self.tb_NF_period = customtkinter.CTkEntry(filePeriodSpecFrame, textvariable=self.NF_period)
        self.tb_NF_period.pack(side=LEFT, fill=BOTH, expand=1)

        paramSpecFrame = customtkinter.CTkFrame(master)
        paramSpecFrame.pack(side=TOP, fill=BOTH)

        self.lbl_Comp_lvl = customtkinter.CTkLabel(paramSpecFrame, text="Comp. level: ")
        self.lbl_Comp_lvl.pack(side=LEFT)
        self.tb_Comp_lvl = customtkinter.CTkEntry(paramSpecFrame, textvariable=self.Comp_lvl)
        self.tb_Comp_lvl.pack(side=LEFT, fill=BOTH, expand=1)
        #self.lbl_maxE = customtkinter.CTkLabel(energy_max_Frame, text="Max E:")
        #self.lbl_maxE.pack(side=LEFT)
        #self.tb_maxE = customtkinter.CTkEntry(energy_max_Frame, textvariable=self.Max_Energy)
        #self.tb_maxE.pack(side=LEFT, fill=BOTH, expand=1)


        self.btn_sel_acq_path = customtkinter.CTkButton(master, text="Acquisition start", command=self.Acq_StartStop_Click)
        self.btn_sel_acq_path.pack(side=TOP, fill=BOTH)

    def SelectFile_click(self):
        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        #Show save file dialog
        self.clusteredFilePath = fd.asksaveasfile(title='Choose measurement file destination', filetypes=filetypes)
        
        self.tb_ClusFilePath.configure(state = "normal")
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.clusteredFilePath.name)[1]) 
        self.tb_ClusFilePath.configure(state = "disabled")

    def Acq_StartStop_Click(self):      
        pass
        #filetypes = (('pickle files', '*.pickle'), ('All files', '*.*'))
        #Show save file dialog
        #processed_fileName = fd.asksaveasfile(initialfile = 'Untitled.pickle', defaultextension=".pickle",filetypes=filetypes)
        #Process
        #global processedData
        #processedData = histogram_matrix_v2(256, 256, self.Max_Energy.get(), self.TimeStep.get())
        #histogram_matrix_v2.getProcessedData(processedData, self.clusteredFilePath, processed_fileName.name)

 
class ProcessedFileLoad:
    def __init__(self, master):
        #Variables
        self.processedFilePath = ""
        #UI
        self.lbl_SelClusFile = customtkinter.CTkLabel(master,text='Select processed file:')
        self.lbl_SelClusFile.pack(side=TOP, fill=BOTH, pady=(30,0))
        selFileFrame = customtkinter.CTkFrame(master)
        selFileFrame.pack(side=TOP)
        self.tb_ClusFilePath = customtkinter.CTkEntry(selFileFrame, state="disabled")
        self.tb_ClusFilePath.pack(side=LEFT, fill=BOTH)
        self.btn_sel_clusFile = customtkinter.CTkButton(selFileFrame, text="Select", command=self.selProcesssedFile_click)
        self.btn_sel_clusFile.pack(side=LEFT, fill=BOTH)
        self.btn_process_clusFile = customtkinter.CTkButton(master, text="Load File", command=self.loadProcessedFile_click)
        self.btn_process_clusFile.pack(side=TOP, fill=BOTH)

    def selProcesssedFile_click(self):
        filetypes = (('pickle files', '*.pickle'), ('All files', '*.*'))
        #Show open file dialog
        self.processedFilePath = fd.askopenfilename(title='Select a processed file', filetypes=filetypes)   

        self.tb_ClusFilePath["state"] = "normal"
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.processedFilePath)[1])  
        self.tb_ClusFilePath["state"] = "disabled"

    def loadProcessedFile_click(self):
        picklefile = open(self.processedFilePath, 'rb')
        global processedData
        processedData = pickle.load(picklefile)

acq_ctrl_box = AcquisitionSetup(CtrlFrame)
conn_ctrl_box = ConnectionPannelContents(ConnectionPannel_Frame)

histogram = np.zeros(10000)
BUFFER = []
def updateData():
    global GUI_hist
    #while(True):
        #item = gui_queue.get()
        #if item is None:
        #    break
        #else:
         #   pass
    TKG.show_plot(np.linspace(1,GUI_hist.maximum, GUI_hist.size), GUI_hist.hist)
            #BUFFER.append(item)
            #Give it to the GUI
            #if(len(BUFFER) >= 1000):    
                #TKG.show_hist(BUFFER)
             #   BUFFER.clear()

    timer = root.after(10000, updateData)

        #plt.hist(item, bins=2000, color='b', label='cesium')
        #plt.hist(list_data, bins=5, color='r', label='neco2')
        #plt.legend(loc = 'upper left')
        #plt.xlabel('Time (ns)', fontsize='large')
        #plt.ylabel('(-)', fontsize='large')
        #plt.grid()
        #plt.xlim(0,10000)
        #plt.show()


timer = root.after(10000, updateData)

root.mainloop()