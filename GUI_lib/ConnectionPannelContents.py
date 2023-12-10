from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
import GUI_lib.floatSpinBox as floatSpinBox

class ConnectionPannelContents:
    def __init__(self, master, communication, gui_queue):
        #Variables
        self.COM_NAME = StringVar()
        self.communication = communication
        self.gui_queue = gui_queue
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
        #global communication
        state = None
        try:
            state = self.communication.ser.is_open
        except:
            state = None

        if( state == None):
            if(self.communication.COM_NAME != None):
                self.communication.COM_connect(str(self.communication.COM_NAME))
        else: 
            if(state == True):
                self.communication.COM_close()
            else: 
                self.communication.COM_connect(str(self.communication.COM_NAME))


        try:
            state = self.communication.ser.is_open
        except:
            state = None

        if(state != None):
            if(state == True):
                self.btn_Connect.configure(text="Close")

                #Start the reception
                self.communication.COM_Receive_Start(self.gui_queue)

            else: 
                self.btn_Connect.configure(text="Connect")
                self.communication.COM_Receive_Stop()
        else: 
            self.btn_Connect.configure(text="Connect")
            self.communication.COM_Receive_Stop()


    def COM_changed(self, port):
        #global communication
        self.communication.COM_NAME = self.cb_selCOM.get()

    def Refresh_click(self):
        #global communication
        self.communication.refresh()# STM_serial(115200)
        self.cb_selCOM.configure(values = self.communication.COM_ports)
