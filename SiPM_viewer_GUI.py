from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
from PIL import ImageTk,Image
import matplotlib
import matplotlib.pyplot as plt
from tkinter import ttk
import GUI_lib.TkinterGraphing as TkinterGraphing
import os
import GUI_lib.ConnectionPannelContents as CONN_GUI
import GUI_lib.AcquisitionSetup as ACQ_GUI
import Communication_lib.STM_serial as SERIAL
from Histogram import *
import Communication_lib.MeasStore as Storage
import Communication_lib.CTRL_MSG as MSG

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


##Set Appearance
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

##Set root and title
root = customtkinter.CTk()
root.title("SiPM Acquisition Control")

###############################################################################
#################################----VARIABLES-----############################

##Object handeling data saving
DataSave = Storage.MeasStore(os.path.expanduser('~/Documents'))
##Communication object
communication = SERIAL.STM_serial(115200, DataSave)
##Queue for gui data handling
gui_queue = SERIAL.Queue()
##Histogram array
histogram = np.zeros(10000)

###############################################################################
#############################----PANEL LAYOUTS-----############################
RightPannelFrame = customtkinter.CTkFrame(root)
RightPannelFrame.pack(side=RIGHT, fill=BOTH, expand=True)

ConnectionPannel_Frame = customtkinter.CTkFrame(RightPannelFrame)
ConnectionPannel_Frame.pack(side=TOP, fill=BOTH)#, expand=True)

ImageFrame = customtkinter.CTkFrame(RightPannelFrame)
ImageFrame.pack(side=TOP, expand=False)

HistogramFrame = customtkinter.CTkFrame(ImageFrame)
HistogramFrame.pack(side=TOP, fill=None, expand=False)

###############################################################################
##############################----GRAPH WINDOW-----############################
TKG = TkinterGraphing.Tkinter_Graphing(HistogramFrame)


################################################################################################
###############################-----CONTROL PANEL-----##########################################
CtrlFrame = customtkinter.CTkFrame(root)
CtrlFrame.pack(side=LEFT, fill=BOTH, expand=1)

##Add the main object
acq_ctrl_box = ACQ_GUI.AcquisitionSetup(CtrlFrame, DataSave)

##Add the processing selection
proc_type_sel = acq_ctrl_box.processingType(CtrlFrame, communication, MSG.CmdRespBuild)

##Add the DAC control
HV_suply = acq_ctrl_box.HV_set(CtrlFrame, 'HV: ', communication, MSG.CmdRespBuild)

DAC_tab_switch = acq_ctrl_box.DAC_tab(CtrlFrame);
DAC_A_set = acq_ctrl_box.DAC_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName1.get()), 'DAC A', 1, communication, MSG.CmdRespBuild)
DAC_B_set = acq_ctrl_box.DAC_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName1.get()), 'DAC B', 2, communication, MSG.CmdRespBuild)
DAC_C_set = acq_ctrl_box.DAC_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName1.get()), 'DAC C', 3, communication, MSG.CmdRespBuild)

EXT_CMP_A_set = acq_ctrl_box.DAC_ext_cmp_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName2.get()), 'DAC A', 1, communication, MSG.CmdRespBuild)
EXT_CMP_B_set = acq_ctrl_box.DAC_ext_cmp_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName2.get()), 'DAC B', 2, communication, MSG.CmdRespBuild)
EXT_CMP_C_set = acq_ctrl_box.DAC_ext_cmp_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName2.get()), 'DAC C', 3, communication, MSG.CmdRespBuild)

EXT_CMP_A_set = acq_ctrl_box.AMP_VREF_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName3.get()), 'DAC A', 1, communication, MSG.CmdRespBuild)
EXT_CMP_B_set = acq_ctrl_box.AMP_VREF_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName3.get()), 'DAC B', 2, communication, MSG.CmdRespBuild)
EXT_CMP_C_set = acq_ctrl_box.AMP_VREF_set(DAC_tab_switch.tabview.tab(DAC_tab_switch.tabName3.get()), 'DAC C', 3, communication, MSG.CmdRespBuild)



##Add the acquisition button
acqBtn = acq_ctrl_box.acquisitionButton(CtrlFrame, communication, MSG.CmdRespBuild, GUI_hist)

##Add the DAC views
dac_ch3_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC C: [mV]")
dac_ch2_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC B: [mV]")
dac_ch1_view = acq_ctrl_box.DAC_view(CtrlFrame, "DAC A: [mV]")

hv_info_view = acq_ctrl_box.HV_view(CtrlFrame)

################################################################################################
###############################-----CONNECTION PANEL-----#######################################
conn_ctrl_box = CONN_GUI.ConnectionPannelContents(ConnectionPannel_Frame, communication, gui_queue)

################################################################################################
####################################-----GUI REFRESH-----#######################################
def updateData():
    global GUI_hist
    
    #Refresh the histogram
    TKG.show_plot(np.linspace(1,GUI_hist.maximum, GUI_hist.size), GUI_hist.hist) 

    #Update DACs
    dac_ch1_view.set_DAC_val(MSG.CTRL_MSG.DAC_A_val)
    dac_ch2_view.set_DAC_val(MSG.CTRL_MSG.DAC_B_val)
    dac_ch3_view.set_DAC_val(MSG.CTRL_MSG.DAC_C_val)

    #Update Acq status
    acqBtn.updateAcqStatus(MSG.CTRL_MSG.measRunning)

    #Update HV info
    hv_info_view.set_HV_val(MSG.CTRL_MSG.HV_value)
    HV_suply.cb_HV_check_update(MSG.CTRL_MSG.HV_state)

    #Update device status
    MSG.boardAliveWDG()
    conn_ctrl_box.updateDeviceState(MSG.CTRL_MSG.boardAlive)

    #Update the processing type
    proc_type_sel.UpdateProcessingType(MSG.CTRL_MSG.processingType)

    #Start again after 1000ms
    timer = root.after(1000, updateData)

##Start the refresh for the first time
timer = root.after(1000, updateData)

##Main tkinter loop
root.mainloop()
