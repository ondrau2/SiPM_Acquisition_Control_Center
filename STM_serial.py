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
from MeasStore import *
from dataclasses import dataclass
import SerialMessage
import CTRL_MSG

TARGET_PATH = os.path.expanduser('~/Documents')
stopEvent = Event()

@dataclass
class detector_event:
    channel: int 
    duration: int

 

class STM_serial:
    def __init__(self, BAUDRATE):
        self.baudrate = 115200
        self.ports = serial.tools.list_ports.comports()
        self.COM_ports = []
        self.ser = None
        self.COM_NAME = None
        for port, desc, hwid in sorted(self.ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            self.COM_ports.append(port)
        
    def COM_connect(self, COM_NAME):
        #try:
            self.ser = serial.Serial(port=COM_NAME, baudrate=self.baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        #except:
        #    print("Error")
    def COM_close(self):
        self.ser.close()

    def transmitt_data(self, data):
        self.ser.write(data)

    def COM_Receive_data_async(self, queue, stopEvent: Event):
        RxMsg = SerialMessage.SerialMessage()

        while (1):
            try:
                state = self.ser.is_open
            except:
                state = None
            if(state != None):
                bytesToRead = self.ser.inWaiting()
                if(bytesToRead > 0):
                    #line = self.ser.readline().decode("utf-8")#(self.ser.readline().decode("utf-8")).split('\r\n')
                    data =  self.ser.read(7)

                    ##Add to buffer and check if complete
                    if(RxMsg.AddRxBytesRoBuffer(data, 7)==True):
                        #Put to queue
                        queue.put(RxMsg)

            if(stopEvent.is_set()):
                break


    def COM_Read_Data_From_Queue(self, queue, GUI_Queue,stopEvent: Event):
        BUFFER_Meas = []
        BUFFER_CTRL = []

        global GUI_hist

        #ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        #path = TARGET_PATH + '\\' + str(ct) + '.txt'

        #global hist
        while True:
            # get a unit of work
            item = queue.get()
            # check for stop
            if item is None:
                break
            else:
                if(item.header == SerialMessage.RxMsgID.measured_pulse_val):
                    measuredVal = (np.uint8(item.data[3])<<24 ) | (np.uint8(item.data[2])<<16 ) | (np.uint8(item.data[1])<<8 ) |np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)
                    #Give it to the GUI
                    if(len(BUFFER_Meas) >= 100):
                        DataSave.SaveBuffer(BUFFER_Meas, "_CH1")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                    GUI_hitcnts.addCount(1, 1)
                else:
                    #BUFFER_CTRL.append(item)
                    #Give it to the GUI thread
                    CTRL_MSG.handle_Rx_CTRL_Msg(item.header, item.data)
                    #BUFFER_CTRL.clear()                   
                
            if(stopEvent.is_set()):
                break

            # report
            #print(f'>Reader got {item}')
    def COM_Receive_Start(self, GUI_queue):
        # create the shared queue
        queue = Queue()
        stopEvent.clear()
        # start the consumer
        my_consumer = Thread(target=self.COM_Read_Data_From_Queue, args=( queue,GUI_queue, stopEvent, ))
        my_consumer.start()
        # start the producer
        my_producer = Thread(target=self.COM_Receive_data_async, args=(queue,stopEvent, ))
        my_producer.start()

    def COM_Receive_Stop(self):
        stopEvent.set()