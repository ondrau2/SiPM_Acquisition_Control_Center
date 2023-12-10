from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
import os
import GUI_lib.floatSpinBox as floatSpinBox

## Components related to the measurement setup - intended for the left pannel
class AcquisitionSetup:
    def __init__(self, master, dataSave):
        #Variables
        self.clusteredFilePath = ""
        self.DataSave = dataSave
        #UI
        #Dummy: single side padding bug - add dummy empty label
        self.lbl_dummyPad1 = customtkinter.CTkLabel(master,text='')
        self.lbl_dummyPad1.pack(side=TOP, fill=BOTH)
        
        #File output gui
        self.lbl_SelClusFile = customtkinter.CTkLabel(master,text='Select measurement file name:')
        self.lbl_SelClusFile.pack(side=TOP, fill=BOTH)
        selFileFrame = customtkinter.CTkFrame(master)
        selFileFrame.pack(side=TOP)
        self.tb_ClusFilePath = customtkinter.CTkEntry(selFileFrame, state="disabled")
        self.tb_ClusFilePath.pack(side=LEFT, fill=BOTH)
        self.btn_sel_clusFile = customtkinter.CTkButton(selFileFrame, text="Select", command=self.SelectFile_click)
        self.btn_sel_clusFile.pack(side=LEFT, fill=BOTH)
        self.lbl_dummyPad2 = customtkinter.CTkLabel(master,text='')
        self.lbl_dummyPad2.pack(side=TOP, fill=BOTH)

    # handle the select button - show the save file dialog
    def SelectFile_click(self):

        filetypes = (('text files', '*.txt'), ('All files', '*.*'))

        #Show save file dialog
        self.clusteredFilePath = fd.asksaveasfile(title='Choose measurement file destination', filetypes=filetypes)
        
        self.tb_ClusFilePath.configure(state = "normal")
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.clusteredFilePath.name)[1]) 
        self.tb_ClusFilePath.configure(state = "disabled")

        self.DataSave.ChangeTargetAddress(self.clusteredFilePath.name)

    # Sub-class for the acquisition button and its functions
    class acquisitionButton:
        def __init__(self, master, communication,CmdRespBuild, GUI_hist) -> None:
            self.communication = communication
            self.CmdRespBuild = CmdRespBuild
            self.GUI_hist = GUI_hist
            self.AcqRunning = False

            #Btn
            self.btn_start_acq = customtkinter.CTkButton(master, text="Acquisition start", command=self.Acq_StartStop_Click)
            self.btn_start_acq.pack(side=TOP, fill=BOTH, pady=20)

        #Button click event
        def Acq_StartStop_Click(self):      
            
            #Check if serial port open
            try:
                state = self.communication.ser.is_open
            except:
                state = None

            #If open handle the strat/stop
            if(state != None):
                tx_arr = self.CmdRespBuild.MeasurementStart_Stop()
                self.communication.transmitt_data(tx_arr)

                if(self.AcqRunning == False):                    
                    self.AcqRunning = True
                    self.btn_start_acq.configure(text = "Stop acquisition")
                    self.GUI_hist.clearHist()

                else: 
                    self.AcqRunning = False
                    self.btn_start_acq.configure(text = "Start acquisition")

        #Update the appearance according to the meas. state
        def updateAcqStatus(self, board_Rx_ack_state):
            #print(str(board_Rx_ack_state))
            if(board_Rx_ack_state == True):
                self.btn_start_acq.configure(text = "Stop acquisition")
            else:
                self.btn_start_acq.configure(text = "Start acquisition")

            self.AcqRunning = board_Rx_ack_state

    #GUI for processing type selection
    class processingType:
        def __init__(self, master, communication, CmdRespBuild) -> None:
            self.communication = communication
            self.CmdRespBuild = CmdRespBuild

            procTypeFrame = customtkinter.CTkFrame(master)
            procTypeFrame.pack(side=TOP, fill=BOTH, pady=10)
            self.ProcType = StringVar()
            self.lbl_prompt = customtkinter.CTkLabel(procTypeFrame,text='Processing method: ')
            self.lbl_prompt.pack(side=LEFT, fill=BOTH)
            self.cb_selProc = customtkinter.CTkComboBox(procTypeFrame, variable=self.ProcType, command= self.ProcTypeChanged)
            self.cb_selProc.configure(values = ["raw_TOT", "exponential_fit", "[NA] linear_fit", "[NA] NN"])
            self.cb_selProc.configure(state = 'readonly')
            self.cb_selProc.pack(side=RIGHT, fill=BOTH)
            self.cb_selProc.bind('<<ComboBoxSelected>>', self.ProcTypeChanged)

        #Handle the selection - send the command
        def ProcTypeChanged(self, dummy):
            procTypeSel = self.cb_selProc.get()
            tx_arr = self.CmdRespBuild.build_processing_type_request(procTypeSel)
            self.communication.transmitt_data(tx_arr)

    #GUI for DAC voltage setting
    class DAC_set:
        def __init__(self, master, channel_lbl, channel_num, communication, CmdRespBuild):
            self.communication = communication
            self.Comp_lvl = DoubleVar()
            self.CH_num = channel_num
            self.CmdRespBuild = CmdRespBuild

            paramSpecFrame = customtkinter.CTkFrame(master)
            paramSpecFrame.pack(side=TOP, fill=BOTH, pady=2)

            self.lbl_Comp_lvl = customtkinter.CTkLabel(paramSpecFrame, text=str(channel_lbl) )
            self.lbl_Comp_lvl.pack(side=LEFT)
            self.tb_Comp_lvl = customtkinter.CTkEntry(paramSpecFrame, textvariable=self.Comp_lvl)
            self.tb_Comp_lvl.pack(side=LEFT, fill=BOTH, expand=1)

            self.btn_start_acq = customtkinter.CTkButton(paramSpecFrame, text="Set", command=self.SetDAC)
            self.btn_start_acq.pack(side=LEFT, fill=BOTH)

        #Set button handle - send the command
        def SetDAC(self):
            tx_arr = self.CmdRespBuild.build_DAC_set_request(self.CH_num, self.Comp_lvl.get())
            self.communication.transmitt_data(tx_arr)
            
    #GUI for the DAC voltage view
    class DAC_view:
        def __init__(self, master, CH):
            self.DAC_voltage = IntVar(value=0) 
            DAC_info = customtkinter.CTkFrame(master)
            DAC_info.pack(side=BOTTOM, fill=BOTH)

            self.lbl_dac_val = customtkinter.CTkLabel(DAC_info, text= CH )
            self.lbl_dac_val.pack(side=LEFT)
            self.tb_dac_val = customtkinter.CTkLabel(DAC_info, text=str(self.DAC_voltage.get()))
            self.tb_dac_val.pack(side=LEFT, fill=BOTH, expand=1)

        #Change the label value
        def set_DAC_val(self, DAC_val):
            self.DAC_voltage = DAC_val
            self.tb_dac_val.configure(text = str(DAC_val))
            

    