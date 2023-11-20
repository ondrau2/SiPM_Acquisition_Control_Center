"""
dataframe:
#,STM_ID,data[8]\r\n
#,STM_ID, data[8]\r\n
#,STM_ID, data[8]\r\n

data - time in ps
"""

import serial
import serial.tools.list_ports
import numpy as np
from scipy import signal
import statistics
import matplotlib.pyplot as plt
import warnings
import datetime
from time import sleep
from random import random
from threading import Thread, Event
from queue import Queue
from Histogram import *
import re
from MeasStore import *
from dataclasses import dataclass

TARGET_PATH = r'C:\Users\ondra\Documents\Projekty\INNMEDSCAN\Technical\data'
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
    def COM_Receive_data_async(self, queue, stopEvent: Event):
        while (1):
            try:
                state = self.ser.is_open
            except:
                state = None
            if(state != None):
                line = self.ser.readline().decode("utf-8")#(self.ser.readline().decode("utf-8")).split('\r\n')
                try:
                    #Filter by channel (TIMA, TIMB, TIMC)
                    if("TIMA" in line):
                        val = detector_event(1, int(re.sub(r'[^0-9]', '', line)))
                        queue.put(val)
                    elif("TIMB" in line):
                        val = detector_event(2, int(re.sub(r'[^0-9]', '', line)))
                        queue.put(val)
                    elif("TIMC" in line):
                        val = detector_event(3, int(re.sub(r'[^0-9]', '', line)))
                        queue.put(val)
                except:
                    pass

            if(stopEvent.is_set()):
                break

            #line = random()*10000

            #print(line[0])
            #queue.put(line[0]);
            #sleep(1)

    def COM_Read_Data_From_Queue(self, queue, GUI_Queue,stopEvent: Event):
        BUFFER_Ch1 = []
        BUFFER_Ch2 = []
        BUFFER_Ch3 = []
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
                if(item.channel == 1):
                    BUFFER_Ch1.append(item.duration)
                    #Give it to the GUI
                    if(len(BUFFER_Ch1) >= 100):
                        DataSave.SaveBuffer(BUFFER_Ch1, "_CH1")
                        GUI_hist.addToHist(BUFFER_Ch1)
                        BUFFER_Ch1.clear()
                    GUI_hitcnts.addCount(1, 1)
                elif(item.channel == 2):
                    BUFFER_Ch2.append(item.duration)
                    #Give it to the GUI
                    if(len(BUFFER_Ch2) >= 100):
                        DataSave.SaveBuffer(BUFFER_Ch2, "_CH2")
                        GUI_hist.addToHist(BUFFER_Ch2)
                        BUFFER_Ch2.clear()                   
                    GUI_hitcnts.addCount(2, 1)
                elif(item.channel == 3):
                    BUFFER_Ch3.append(item.duration)
                    #Give it to the GUI
                    if(len(BUFFER_Ch3) >= 100):
                        DataSave.SaveBuffer(BUFFER_Ch3, "_CH3")
                        GUI_hist.addToHist(BUFFER_Ch3)
                        BUFFER_Ch3.clear()                    
                    GUI_hitcnts.addCount(3, 1)

                

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