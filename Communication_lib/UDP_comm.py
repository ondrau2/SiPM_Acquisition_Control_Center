import socket
import numpy as np
from threading import Thread, Event
from queue import Queue
import Communication_lib.SerialMessage as SerialMessage
import Communication_lib.CTRL_MSG as CTRL_MSG
from Histogram import *

##UDP reception class
class UDP_comm:
    def __init__(self, DataSave):
        self.UDP_IP = "0.0.0.0"
        self.UDP_PORT = 5005
        self.sock = None
        self.DataSave = DataSave
        self.connected = False
        self.stopEvent = Event()
        self.producer_thread = None
        self.consumer_thread = None
        
    #Set UDP parameters
    def set_UDP_params(self, ip, port):
        self.UDP_IP = ip
        self.UDP_PORT = port
    
    #Connect to UDP
    def UDP_connect(self):
        try:
            if self.sock:
                self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.UDP_IP, self.UDP_PORT))
            self.sock.settimeout(1.0)  # 1 second timeout for checking stop event
            self.connected = True
            return True
        except OSError as e:
            print(f"UDP connection error: {e}")
            # WinError 10049: The requested address is not valid in its context
            if hasattr(e, 'winerror') and e.winerror == 10049:
                print(f"IP {self.UDP_IP} invalid for local bind. Trying 0.0.0.0")
                try:
                    self.sock.close()
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock.bind(("0.0.0.0", self.UDP_PORT))
                    self.sock.settimeout(1.0)
                    self.connected = True
                    return True
                except Exception as e2:
                    print(f"UDP fallback connection error: {e2}")

            self.connected = False
            return False
        except Exception as e:
            print(f"UDP connection error: {e}")
            self.connected = False
            return False
    
    #Close the UDP socket
    def UDP_close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        self.connected = False
    
    #Check if connected
    def is_open(self):
        return self.connected
    
    #Transmit data via UDP (if needed for commands)
    def transmitt_data(self, data):
        # For UDP, we might need to send to a specific target address
        # This can be configured if needed
        pass
    
    #Asynchronous reception
    def UDP_Receive_data_async(self, queue, stopEvent: Event):
        while True:
            try:
                # Receive data with timeout
                data, addr = self.sock.recvfrom(1024)
                
                if len(data) >= 7:
                    RxMsg = SerialMessage.SerialMessage()
                    
                    # Process 7-byte packets
                    for i in range(0, len(data), 7):
                        if i + 7 <= len(data):
                            packet = data[i:i+7]
                            
                            # Add to buffer and check if complete
                            if RxMsg.AddRxBytesRoBuffer(packet, 7):
                                # Put to queue - other thread reads
                                queue.put(RxMsg)
                                RxMsg = SerialMessage.SerialMessage()
                                
            except socket.timeout:
                # Timeout is normal, just check for stop event
                pass
            except Exception as e:
                if self.connected:  # Only print if we're still supposed to be connected
                    print(f"UDP receive error: {e}")
            
            # Check if stop is requested
            if stopEvent.is_set():
                break
    
    ##Read from the queue and store to buffer             
    def UDP_Read_Data_From_Queue(self, queue, GUI_Queue, stopEvent: Event):
        BUFFER_Meas = []
        
        BUFFER_Meas_A = []
        BUFFER_Meas_B = []
        BUFFER_Meas_C = []
        BUFFER_CTRL = []

        # Use global histogram object
        global GUI_hist

        A_cnt = 0
        B_cnt = 0
        C_cnt = 0

        while True:
            # Check if stop requested first
            if stopEvent.is_set():
                break
                
            # Measurement and control message buffers
            try:
                item = queue.get(block=True, timeout=0.5)
            except:
                # Timeout - check stop event and continue
                continue

            # Check if exists
            if item is None:
                break
            else:
                # Check if message is measurement
                if item.header == SerialMessage.RxMsgID.measured_pulse_val.value:
                    measuredVal = (np.uint8(item.data[3])<<24) | (np.uint8(item.data[2])<<16) | (np.uint8(item.data[1])<<8) | np.uint8(item.data[0])
                    BUFFER_Meas.append(measuredVal)

                    # Read the buffer when decent amount of data
                    if len(BUFFER_Meas) >= 1:
                        self.DataSave.SaveBuffer(BUFFER_Meas, "_tot")
                        GUI_hist.addToHist(BUFFER_Meas)
                        BUFFER_Meas.clear()
                elif item.header == SerialMessage.RxMsgID.measured_ch_A.value:
                    measuredVal = (np.uint8(item.data[3])<<24) | (np.uint8(item.data[2])<<16) | (np.uint8(item.data[1])<<8) | np.uint8(item.data[0])
                    BUFFER_Meas_A.append(measuredVal)
                    A_cnt = A_cnt + 1
                    # Read the buffer when decent amount of data
                    if len(BUFFER_Meas_A) >= 1:
                        self.DataSave.SaveBuffer(BUFFER_Meas_A, "_CH1")
                        GUI_hist.addToHist(BUFFER_Meas_A)
                        BUFFER_Meas_A.clear()
                elif item.header == SerialMessage.RxMsgID.measured_ch_B.value:
                    measuredVal = (np.uint8(item.data[3])<<24) | (np.uint8(item.data[2])<<16) | (np.uint8(item.data[1])<<8) | np.uint8(item.data[0])
                    BUFFER_Meas_B.append(measuredVal)
                    B_cnt = B_cnt + 1

                    # Read the buffer when decent amount of data
                    if len(BUFFER_Meas_B) >= 1:
                        self.DataSave.SaveBuffer(BUFFER_Meas_B, "_CH2")
                        GUI_hist.addToHist(BUFFER_Meas_B)
                        BUFFER_Meas_B.clear()
                elif item.header == SerialMessage.RxMsgID.measured_ch_C.value:
                    measuredVal = (np.uint8(item.data[3])<<24) | (np.uint8(item.data[2])<<16) | (np.uint8(item.data[1])<<8) | np.uint8(item.data[0])
                    BUFFER_Meas_C.append(measuredVal)
                    C_cnt = C_cnt + 1

                    # Read the buffer when decent amount of data
                    if len(BUFFER_Meas_C) >= 1:
                        self.DataSave.SaveBuffer(BUFFER_Meas_C, "_CH3")
                        GUI_hist.addToHist(BUFFER_Meas_C)
                        BUFFER_Meas_C.clear()
                else:
                    # Control message - handle directly
                    CTRL_MSG.handle_Rx_CTRL_Msg(item.header, item.data)

    ##Start the reception
    def UDP_Receive_Start(self, GUI_queue):
        # Create the shared queue
        queue = Queue()
        self.stopEvent.clear()
        # Create the consumer
        self.consumer_thread = Thread(target=self.UDP_Read_Data_From_Queue, args=(queue, GUI_queue, self.stopEvent,))
        self.consumer_thread.start()
        # Start the rx
        self.producer_thread = Thread(target=self.UDP_Receive_data_async, args=(queue, self.stopEvent,))
        self.producer_thread.start()

    # Stop the async receive
    def UDP_Receive_Stop(self):
        self.stopEvent.set()
        # Wait for threads to complete with timeout
        if self.producer_thread is not None:
            self.producer_thread.join(timeout=2.0)
            self.producer_thread = None
        if self.consumer_thread is not None:
            self.consumer_thread.join(timeout=2.0)
            self.consumer_thread = None
