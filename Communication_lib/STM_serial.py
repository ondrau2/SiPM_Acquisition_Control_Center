import serial
import serial.tools.list_ports
import numpy as np
from scipy import signal
import statistics
import matplotlib.pyplot as plt
import warnings
import datetime
import os
from time import sleep
from random import random
from threading import Thread, Event
from queue import Queue
from Histogram import *
import re
#from MeasStore import *
from dataclasses import dataclass
import Communication_lib.SerialMessage as SerialMessage
import Communication_lib.CTRL_MSG as CTRL_MSG

##Stop the async Rx
stopEvent = Event()

"""@dataclass
class detector_event:
    channel: int 
    duration: int"""

 
##Serial reception class
class STM_serial:
    def __init__(self, BAUDRATE, DataSave):
        self.baudrate = 115200
        self.ports = serial.tools.list_ports.comports()
        self.COM_ports = []
        self.ser = None
        self.COM_NAME = None
        self.DataSave = DataSave
        for port, desc, hwid in sorted(self.ports):
            #print("{}: {} [{}]".format(port, desc, hwid))
            self.COM_ports.append(port)
        
    #Refresh the ports
    def refresh(self):
        self.COM_ports = []
        self.ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(self.ports):
            #print("{}: {} [{}]".format(port, desc, hwid))
            self.COM_ports.append(port)

    #Connect to the port
    def COM_connect(self, COM_NAME):
        self.ser = serial.Serial(port=COM_NAME, baudrate=self.baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

    #Closse the COM port
    def COM_close(self):
        self.ser.close()

    #Transmitt data
    def transmitt_data(self, data):
        self.ser.write(data)

    #Asynchronnous reception
    def COM_Receive_data_async(self, queue, stopEvent: Event):
        RxMsg = SerialMessage.SerialMessage()

        while (1):
            try:            
                bytesToRead = self.ser.inWaiting()
                if(bytesToRead > 0):
                    #Read 7 bytes
                    data =  self.ser.read(7)

                    #Add to buffer and check if complete
                    if(RxMsg.AddRxBytesRoBuffer(data, 7)==True):
                        #Put to queue - other thread reads
                        queue.put(RxMsg)
            except:
                pass

            #Check if stop is requested
            if(stopEvent.is_set()):
                break

    ##Read from the queue and store to buffer             
    def COM_Read_Data_From_Queue(self, queue, GUI_Queue,stopEvent: Event):

        #Measurement and control message buffers
        BUFFER_Meas = []
        BUFFER_CTRL = []

        #Use global histogram object
        global GUI_hist

        while True:

            item = queue.get()

            #Check if exists
            if item is None:
                break
            else:
                #Check if message is measurement
                if(item.header == SerialMessage.RxMsgID.measured_pulse_val):
                    measuredVal = (np.uint8(item.data[3])<<24 ) | (np.uint8(item.data[2])<<16 ) | (np.uint8(item.data[1])<<8 ) |np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)

                    #Read the buffer when decent amount of data
                    if(len(BUFFER_Meas) >= 100):
                        self.DataSave.SaveBuffer(BUFFER_Meas, "_CH1")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                elif(item.header == SerialMessage.RxMsgID.measured_ch_A):
                    measuredVal = (np.uint8(item.data[3])<<24 ) | (np.uint8(item.data[2])<<16 ) | (np.uint8(item.data[1])<<8 ) |np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)

                    #Read the buffer when decent amount of data
                    if(len(BUFFER_Meas) >= 100):
                        self.DataSave.SaveBuffer(BUFFER_Meas, "_CH1")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                elif(item.header == SerialMessage.RxMsgID.measured_ch_B):
                    measuredVal = (np.uint8(item.data[3])<<24 ) | (np.uint8(item.data[2])<<16 ) | (np.uint8(item.data[1])<<8 ) |np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)

                    #Read the buffer when decent amount of data
                    if(len(BUFFER_Meas) >= 100):
                        self.DataSave.SaveBuffer(BUFFER_Meas, "_CH2")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                elif(item.header == SerialMessage.RxMsgID.measured_ch_C):
                    measuredVal = (np.uint8(item.data[3])<<24 ) | (np.uint8(item.data[2])<<16 ) | (np.uint8(item.data[1])<<8 ) |np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)

                    #Read the buffer when decent amount of data
                    if(len(BUFFER_Meas) >= 100):
                        self.DataSave.SaveBuffer(BUFFER_Meas, "_CH3")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                else:
                    #Control message - handle directly
                    CTRL_MSG.handle_Rx_CTRL_Msg(item.header, item.data)
                
            #Check if stop requested
            if(stopEvent.is_set()):
                break

    ##Start the reception
    def COM_Receive_Start(self, GUI_queue):
        #Create the shared queue
        queue = Queue()
        stopEvent.clear()
        #Create the consumer
        my_consumer = Thread(target=self.COM_Read_Data_From_Queue, args=( queue,GUI_queue, stopEvent, ))
        my_consumer.start()
        #Start the rx
        my_producer = Thread(target=self.COM_Receive_data_async, args=(queue,stopEvent, ))
        my_producer.start()

    #Stop the async receive
    def COM_Receive_Stop(self):
        stopEvent.set()