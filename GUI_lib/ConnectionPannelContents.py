from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
import GUI_lib.floatSpinBox as floatSpinBox

##GUI for COM port connection panel (top of the app)
class ConnectionPannelContents:
    def __init__(self, master, communication, gui_queue, udp_communication=None):
        #Variables
        self.COM_NAME = StringVar()
        self.communication = communication
        self.udp_communication = udp_communication
        self.gui_queue = gui_queue
        self.connection_type = StringVar(value="Serial")
        
        #Connection type selection
        self.lbl_conn_type = customtkinter.CTkLabel(master, text='Connection: ')
        self.lbl_conn_type.pack(side=LEFT, fill=BOTH)
        
        self.cb_conn_type = customtkinter.CTkComboBox(master, variable=self.connection_type, 
                                                       command=self.conn_type_changed,
                                                       values=["Serial", "UDP"])
        self.cb_conn_type.configure(state='readonly')
        self.cb_conn_type.pack(side=LEFT, fill=BOTH)
        
        #Serial-specific widgets
        self.lbl_COM_name = customtkinter.CTkLabel(master, text='COM port: ')
        self.lbl_COM_name.pack(side=LEFT, fill=BOTH)

        self.cb_selCOM = customtkinter.CTkComboBox(master, variable=self.COM_NAME, command=self.COM_changed)
        self.cb_selCOM.configure(values=["dummy1", "dummy2", "dummy3", "dummy4"])
        self.cb_selCOM.configure(state='readonly')
        self.cb_selCOM.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM.bind('<<ComboBoxSelected>>', self.COM_changed)

        #UDP-specific widgets (initially hidden)
        self.lbl_UDP_IP = customtkinter.CTkLabel(master, text='Bind IP: ')
        self.entry_UDP_IP = customtkinter.CTkEntry(master, width=100)
        self.entry_UDP_IP.insert(0, "0.0.0.0")
        
        self.lbl_UDP_PORT = customtkinter.CTkLabel(master, text='Port: ')
        self.entry_UDP_PORT = customtkinter.CTkEntry(master, width=80)
        self.entry_UDP_PORT.insert(0, "5005")

        #Refresh button - find COM ports
        self.btn_Refresh = customtkinter.CTkButton(master, text="Refresh", command=self.Refresh_click)
        self.btn_Refresh.pack(side=LEFT, fill=BOTH)

        #Connect/disconnect button
        self.btn_Connect = customtkinter.CTkButton(master, text="Connect", command=self.Connect_click)
        self.btn_Connect.pack(side=LEFT, fill=BOTH)
        
        #Info about the device state
        self.lbl_device_state = customtkinter.CTkLabel(master, text='Device state')
        self.lbl_device_state.pack(side=RIGHT, fill=BOTH)
        self.Refresh_click()
        
        #Update UI based on connection type
        self.update_connection_ui()

    #Update the device state
    def updateDeviceState(self, alive):
        if(alive == True):
            self.lbl_device_state.configure(text = 'Device running')
        else:
            self.lbl_device_state.configure(text = 'Device N/A')
    
    #Update UI based on connection type
    def update_connection_ui(self):
        conn_type = self.connection_type.get()
        
        if conn_type == "Serial":
            # Show serial widgets
            self.lbl_COM_name.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
            self.cb_selCOM.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
            # Hide UDP widgets
            self.lbl_UDP_IP.pack_forget()
            self.entry_UDP_IP.pack_forget()
            self.lbl_UDP_PORT.pack_forget()
            self.entry_UDP_PORT.pack_forget()
        else:  # UDP
            # Hide serial widgets
            self.lbl_COM_name.pack_forget()
            self.cb_selCOM.pack_forget()
            # Show UDP widgets
            self.lbl_UDP_IP.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
            self.entry_UDP_IP.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
            self.lbl_UDP_PORT.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
            self.entry_UDP_PORT.pack(side=LEFT, fill=BOTH, before=self.btn_Refresh)
    
    #Connection type change handler
    def conn_type_changed(self, value):
        self.update_connection_ui()
        # Reset connect button
        self.btn_Connect.configure(text="Connect")
    
    #Handle the connect/close button
    def Connect_click(self):
        conn_type = self.connection_type.get()
        
        if conn_type == "Serial":
            self._connect_serial()
        else:  # UDP
            self._connect_udp()
    
    #Handle serial connection
    def _connect_serial(self):
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
    
    #Handle UDP connection
    def _connect_udp(self):
        if self.udp_communication is None:
            self.lbl_device_state.configure(text='UDP not available')
            return
        
        #Check the status
        state = self.udp_communication.is_open()

        if not state:
            # Not connected - try to connect
            try:
                ip = self.entry_UDP_IP.get()
                port = int(self.entry_UDP_PORT.get())
                
                # Validate port range
                if port < 1 or port > 65535:
                    self.lbl_device_state.configure(text='Invalid port (1-65535)')
                    return
                
                self.udp_communication.set_UDP_params(ip, port)
                
                if self.udp_communication.UDP_connect():
                    self.btn_Connect.configure(text="Close")
                    self.udp_communication.UDP_Receive_Start(self.gui_queue)
                    self.lbl_device_state.configure(text='UDP connected')
                else:
                    self.btn_Connect.configure(text="Connect")
                    self.lbl_device_state.configure(text='UDP connection failed')
            except ValueError:
                self.lbl_device_state.configure(text='Invalid port number')
        else:
            # Connected - close
            self.udp_communication.UDP_Receive_Stop()
            self.udp_communication.UDP_close()
            self.btn_Connect.configure(text="Connect")
            self.lbl_device_state.configure(text='UDP disconnected')

    #COM port combo box change handler
    def COM_changed(self, port):
        self.communication.COM_NAME = self.cb_selCOM.get()

    #COM port refresh handler
    def Refresh_click(self):
        self.communication.refresh()
        self.cb_selCOM.configure(values = self.communication.COM_ports)
