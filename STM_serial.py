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
from threading import Thread
from queue import Queue
from Histogram import *
import re
 
TARGET_PATH = r'C:\Users\ondra\Documents\Projekty\INNMEDSCAN\Technical\data'

class STM_serial:
    def __init__(self, BAUDRATE):
        self.baudrate = 115200
        self.ports = serial.tools.list_ports.comports()
        self.COM_ports = []
        self.ser = None
        for port, desc, hwid in sorted(self.ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            self.COM_ports.append(port)
        
    def COM_connect(self, COM_NAME):
        #try:
            self.ser = serial.Serial(port=COM_NAME, baudrate=self.baudrate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        #except:
        #    print("Error")
    def COM_Receive_data_async(self, queue):
        while (1):
            line = self.ser.readline().decode("utf-8")#(self.ser.readline().decode("utf-8")).split('\r\n')
            try:
                val = int(re.sub(r'[^0-9]', '', line))
                queue.put(val)

            except:
                pass
            #line = random()*10000

            #print(line[0])
            #queue.put(line[0]);
            #sleep(1)

    def COM_Read_Data_From_Queue(self, queue, GUI_Queue):
        BUFFER = []
        global GUI_hist

        ct = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        path = TARGET_PATH + '\\' + str(ct) + '.txt'

        #global hist
        while True:
            # get a unit of work
            item = queue.get()
            # check for stop
            if item is None:
                break
            else:
                BUFFER.append(item)
                #Give it to the GUI
                if(len(BUFFER) >= 1000):
                    with open(path,'a', newline='\n') as file:
                        file.write(','.join(str(i) for i in BUFFER))

                    GUI_hist.addToHist(BUFFER)
                    BUFFER.clear()
                #GUI_Queue.put(item)


            # report
            #print(f'>Reader got {item}')
    def COM_Receive_Start(self, GUI_queue):
        # create the shared queue
        queue = Queue()
        # start the consumer
        my_consumer = Thread(target=self.COM_Read_Data_From_Queue, args=( queue,GUI_queue,))
        my_consumer.start()
        # start the producer
        my_producer = Thread(target=self.COM_Receive_data_async, args=(queue,))
        my_producer.start()