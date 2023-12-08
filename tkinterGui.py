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
from MeasStore import *
import CTRL_MSG

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
root = customtkinter.CTk()
#root.iconbitmap("C:/Users/klesa/Documents/ZCU/INNMEDSCAN/python/SiPM_Acquisition_Control_Center-master/INNMEDSCAN_logo.ico")
root.title("SiPM Acquisition Control")

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
#communication.COM_connect("COM5")
gui_queue = Queue()

#STM_serial.COM_Receive_Start(communication,gui_queue)

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

        self.btn_Refresh = customtkinter.CTkButton(master, text="Refresh", command=self.Refresh_click)
        self.btn_Refresh.pack(side=LEFT, fill=BOTH)

        self.btn_Connect = customtkinter.CTkButton(master, text="Connect", command=self.Connect_click)
        self.btn_Connect.pack(side=LEFT, fill=BOTH)
        
        self.lbl_device_state = customtkinter.CTkLabel(master,text='Device state')
        self.lbl_device_state.pack(side=RIGHT, fill=BOTH)
        self.Refresh_click()

    def updateDeviceState(self, alive):
        if(alive == True):
            self.lbl_device_state.configure(text = 'Device running')
        else:
            self.lbl_device_state.configure(text = 'Device N/A')
    
    def Connect_click(self):
        global communication
        state = None
        try:
            state = communication.ser.is_open
        except:
            state = None

        if( state == None):
            if(communication.COM_NAME != None):
                communication.COM_connect(str(communication.COM_NAME))
        else: 
            if(state == True):
                communication.COM_close()
            else: 
                communication.COM_connect(str(communication.COM_NAME))


        try:
            state = communication.ser.is_open
        except:
            state = None

        if(state != None):
            if(state == True):
                self.btn_Connect.configure(text="Close")

                #Start the reception
                communication.COM_Receive_Start(gui_queue)

            else: 
                self.btn_Connect.configure(text="Connect")
        else: 
            self.btn_Connect.configure(text="Connect")

    def COM_changed(self, port):
        global communication
        communication.COM_NAME = self.cb_selCOM.get()

    def Refresh_click(self):
        global communication
        communication = STM_serial(115200)
        self.cb_selCOM.configure(values = communication.COM_ports)



################################################################################################
###############################-----CONTROL PANEL-----##########################################
CtrlFrame = customtkinter.CTkFrame(root)
CtrlFrame.pack(side=LEFT, fill=BOTH, expand=1)

class AcquisitionSetup:
    def __init__(self, master):
        #Variables
        self.clusteredFilePath = ""
        self.AcqRunning = False
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


        self.btn_start_acq = customtkinter.CTkButton(master, text="Acquisition start", command=self.Acq_StartStop_Click)
        self.btn_start_acq.pack(side=TOP, fill=BOTH)

    #DAC info:
    class DAC_view:
        def __init__(self, master, CH):
            self.DAC_voltage = IntVar(value=0) 
            DAC_info = customtkinter.CTkFrame(master)
            DAC_info.pack(side=BOTTOM, fill=BOTH)

            self.lbl_dac_val = customtkinter.CTkLabel(DAC_info, text= CH )
            self.lbl_dac_val.pack(side=LEFT)
            self.tb_dac_val = customtkinter.CTkLabel(DAC_info, text=str(self.DAC_voltage))
            self.tb_dac_val.pack(side=LEFT, fill=BOTH, expand=1)

        def set_DAC_val(self, DAC_val):
            self.DAC_voltage = DAC_val
            self.tb_dac_val.configure(text = str(DAC_val))
            #self.tb_dac_val.delete(0,tk.END)
            #self.tb_dac_val.insert(0,self.DAC_voltage)

    def SelectFile_click(self):
        global DataSave

        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        #Show save file dialog
        self.clusteredFilePath = fd.asksaveasfile(title='Choose measurement file destination', filetypes=filetypes)
        
        self.tb_ClusFilePath.configure(state = "normal")
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.clusteredFilePath.name)[1]) 
        self.tb_ClusFilePath.configure(state = "disabled")

        DataSave.ChangeTargetAddress(self.clusteredFilePath.name)

    def Acq_StartStop_Click(self):      
        global communication
        try:
            state = communication.ser.is_open
        except:
            state = None

        if(state != None):
            if(self.AcqRunning == False):
                communication.ser.write(acq_ctrl_box.tb_Comp_lvl.get().encode("utf-8"))
                
                GUI_hitcnts.clearCounters()
                communication.COM_Receive_Start(gui_queue)
                self.AcqRunning = True
                self.btn_start_acq.configure(text = "Stop acquisition")
            else: 
                communication.COM_Receive_Stop()
                self.AcqRunning = False
                self.btn_start_acq.configure(text = "Start acquisition")
                GUI_hist.clearHist()

    def updateAcqStatus(self, board_Rx_ack_state):
        if(self.AcqRunning != board_Rx_ack_state):
            #Measurement status not in agreement
            self.AcqRunning = board_Rx_ack_state
            if(self.AcqRunning == True):
                self.btn_start_acq.configure(text = "Stop acquisition")
            else:
                self.btn_start_acq.configure(text = "Start acquisition")

 
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
dac_ch3_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC C: [mV]")
dac_ch2_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC B: [mV]")
dac_ch1_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC A: [mV]")

conn_ctrl_box = ConnectionPannelContents(ConnectionPannel_Frame)

histogram = np.zeros(10000)
BUFFER = []
def updateData():
    global GUI_hist
    
    TKG.show_plot(np.linspace(1,GUI_hist.maximum, GUI_hist.size), GUI_hist.hist) 

    #Update DACs
    dac_ch1_view.set_DAC_val(CTRL_MSG.CTRL_MSG.DAC_A_val)
    dac_ch2_view.set_DAC_val(CTRL_MSG.CTRL_MSG.DAC_A_val)
    dac_ch3_view.set_DAC_val(CTRL_MSG.CTRL_MSG.DAC_A_val)
   
    #Update Acq status
    acq_ctrl_box.updateAcqStatus(CTRL_MSG.CTRL_MSG.measRunning)

    #Update device status
    CTRL_MSG.boardAliveWDG()
    conn_ctrl_box.updateDeviceState(CTRL_MSG.CTRL_MSG.boardAlive)

    timer = root.after(1000, updateData)

        #plt.hist(item, bins=2000, color='b', label='cesium')
        #plt.hist(list_data, bins=5, color='r', label='neco2')
        #plt.legend(loc = 'upper left')
        #plt.xlabel('Time (ns)', fontsize='large')
        #plt.ylabel('(-)', fontsize='large')
        #plt.grid()
        #plt.xlim(0,10000)
        #plt.show()




timer = root.after(1000, updateData)

root.mainloop()
