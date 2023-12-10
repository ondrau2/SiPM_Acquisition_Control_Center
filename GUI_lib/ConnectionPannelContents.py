from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
import GUI_lib.floatSpinBox as floatSpinBox

##GUI for COM port connection panel (top of the app)
class ConnectionPannelContents:
    def __init__(self, master, communication, gui_queue):
        #Variables
        self.COM_NAME = StringVar()
        self.communication = communication
        self.gui_queue = gui_queue
        
        #Label
        self.lbl_COM_name = customtkinter.CTkLabel(master,text='Select the COM port: ')
        self.lbl_COM_name.pack(side=LEFT, fill=BOTH)

        #Combo box
        self.cb_selCOM = customtkinter.CTkComboBox(master, variable=self.COM_NAME, command= self.COM_changed)
        self.cb_selCOM.configure(values = ["dummy1", "dummy2", "dummy3", "dummy4"])
        self.cb_selCOM.configure(state = 'readonly')
        self.cb_selCOM.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM.bind('<<ComboBoxSelected>>', self.COM_changed)

        #Refresh button - find COM ports
        self.btn_Refresh = customtkinter.CTkButton(master, text="Refresh", command=self.Refresh_click)
        self.btn_Refresh.pack(side=LEFT, fill=BOTH)

        #Connect/disconnect button
        self.btn_Connect = customtkinter.CTkButton(master, text="Connect", command=self.Connect_click)
        self.btn_Connect.pack(side=LEFT, fill=BOTH)
        
        #Info about the device state
        self.lbl_device_state = customtkinter.CTkLabel(master,text='Device state')
        self.lbl_device_state.pack(side=RIGHT, fill=BOTH)
        self.Refresh_click()

    #Update the device state
    def updateDeviceState(self, alive):
        if(alive == True):
            self.lbl_device_state.configure(text = 'Device running')
        else:
            self.lbl_device_state.configure(text = 'Device N/A')
    
    #Handle the connect/close button
    def Connect_click(self):
        #Check the status
        state = None
        try:
            state = self.communication.ser.is_open
        except:
            state = None

        if( state == None):
            #If not connected and name exists - connect
            if(self.communication.COM_NAME != None):
                self.communication.COM_connect(str(self.communication.COM_NAME))
        else: 
            #State is True/false - open/close
            if(state == True):
                self.communication.COM_close()
            else: 
                self.communication.COM_connect(str(self.communication.COM_NAME))

        #Check the state again
        try:
            state = self.communication.ser.is_open
        except:
            state = None

        #Set the visuals and start/stop the reception
        if(state != None):
            if(state == True):
                #Connection ok - set visuals and start reception
                self.btn_Connect.configure(text="Close")
                self.communication.COM_Receive_Start(self.gui_queue)

            else: 
                #Connection closed - update visuals and stop reception
                self.btn_Connect.configure(text="Connect")
                self.communication.COM_Receive_Stop()
        else: 
            #Connection not available - update visuals and stop reception
            self.btn_Connect.configure(text="Connect")
            self.communication.COM_Receive_Stop()

    #COM port combo box change handler
    def COM_changed(self, port):
        self.communication.COM_NAME = self.cb_selCOM.get()

    #COM port refresh handler
    def Refresh_click(self):
        self.communication.refresh()
        self.cb_selCOM.configure(values = self.communication.COM_ports)
