from enum import Enum
import numpy as np

###############################################################################
#################################----VARIABLES-----############################

#Packet data length
totalDataLength = 7

#CRC table
crc_table = np.array([
	0,   49,  98,  83,  196, 245, 166, 151, 185, 136, 219, 234, 125, 76,  31,  46,
	67,  114, 33,  16,  135, 182, 229, 212, 250, 203, 152, 169, 62,  15,  92,  109,
	134, 183, 228, 213, 66,  115, 32,  17,  63,  14,  93,  108, 251, 202, 153, 168,
	197, 244, 167, 150, 1,   48,  99,  82,  124, 77,  30,  47,  184, 137, 218, 235,
	61,  12,  95,  110, 249, 200, 155, 170, 132, 181, 230, 215, 64,  113, 34,  19,
	126, 79,  28,  45,  186, 139, 216, 233, 199, 246, 165, 148, 3,   50,  97,  80,
	187, 138, 217, 232, 127, 78,  29,  44,  2,   51,  96,  81,  198, 247, 164, 149,
	248, 201, 154, 171, 60,  13,  94,  111, 65,  112, 35,  18,  133, 180, 231, 214,
	122, 75,  24,  41,  190, 143, 220, 237, 195, 242, 161, 144, 7,   54,  101, 84,
	57,  8,   91,  106, 253, 204, 159, 174, 128, 177, 226, 211, 68,  117, 38,  23,
	252, 205, 158, 175, 56,  9,   90,  107, 69,  116, 39,  22,  129, 176, 227, 210,
	191, 142, 221, 236, 123, 74,  25,  40,  6,   55,  100, 85,  194, 243, 160, 145,
	71,  118, 37,  20,  131, 178, 225, 208, 254, 207, 156, 173, 58,  11,  88,  105,
	4,   53,  102, 87,  192, 241, 162, 147, 189, 140, 223, 238, 121, 72,  27,  42,
	193, 240, 163, 146, 5,   52,  103, 86,  120, 73,  26,  43,  188, 141, 222, 239,
	130, 179, 224, 209, 70,  119, 36,  21,  59,  10,  89,  104, 255, 206, 157, 172
],np.uint8)

#Receive data buffer
rx_data_buff = [0xFF]*totalDataLength*8 

###############################################################################
###############################----MESSAGE IDs-----############################

class RxMsgID(Enum):
    tx_invalid = 0			## Invalid 
    meas_start_ack = 1		## Measurement start acknowledge 
    meas_stop_ack = 2		## Measurement stop acknowledge 
    measured_pulse_val = 3	## Recalculated value of the measured pulse 
    heart_beat = 4			## Periodic message for alive indication 
    DAC_set_resp = 5		## Acknowledgment of DAC voltage setup 
    proc_type_ack = 6		## Acknowledgment of processing type change 
    measured_ch_A = 7       ## Measuremetn data for CH A (CH 1)
    measured_ch_B = 8       ## Measuremetn data for CH B (CH 2)
    measured_ch_C = 9       ## Measuremetn data for CH C (CH 3)
    HV_state = 10           ## State of the HV voltage supply (enable, set V, real V)

class TxMsgID(Enum):
    rx_invalid = 0		## Invalid 
    meas_start_req = 1	## Measurement start request 
    meas_stop_req = 2	    ## Measurement stop request 
    DAC_A_set = 3		    ## DAC channel A voltage set 
    DAC_B_set = 4		    ## DAC channel B voltage set 
    DAC_C_set = 5		    ## DAC channel C voltage set 
    processing_type = 6	    ## Type of the processing change request 
    HV_val_set = 7          ## Set HV 
    HV_enable = 8           ## Enable the HV source

class PulseProcesssingTypes(Enum):
    Independent = 0         ## Independent channels
    raw_TOT = 1			    ## Only ToT evaluation 
    exponential_fit = 2 	## Fit exponential function 
    linear_fit = 3			## Not implemented 
    NN = 4					## Not implemented 

###############################################################################
#######################----DATA HANDLING CALSS-----############################
class SerialMessage:
    def __init__(self):
        self.startSymbol = 0x55
        self.header = 0                ## RxMsgID
        self.data = np.array([0,0,0,0])     ## byte array
        self.crc8 = 0

    #Get CRC of the packet
    def getCRC8(self):
        crc = 0
        data = self.data
        size = np.size(data)

        crc = crc_table[crc ^ self.header.value]
        for i in range(0,size):
            crc = crc_table[crc ^ data[i]]
        self.crc8 = crc

    #Get crc from an array
    def getRawDataCRC8(self, data):
        crc = 0
        size = totalDataLength 
        #Calculate from header to last data byte
        for i in range(1,size-1):
            crc = crc_table[np.bitwise_xor(np.uint8(crc), np.uint8(data[i]))]
        return crc
    
    #Store packet to an array
    def buildByteArr(self):
        dataArr = np.zeros(7, dtype='uint8')
        dataArr[0] = self.startSymbol
        dataArr[1] = self.header.value
        dataArr[2] = self.data[0]
        dataArr[3] = self.data[1]
        dataArr[4] = self.data[2]
        dataArr[5] = self.data[3]
        dataArr[6] = self.crc8

        return dataArr
    
    #Check the message format (from bytes)
    def checkRawMsgFormat(self, data):
        if(data[0] == 0x55):
            if(data[6] == self.getRawDataCRC8(data)):
                return True
        return False
    
    #Builds packet from received bytes
    def buildStructureFromRxData(self, data):
        formatCheck = self.checkRawMsgFormat(data)
        if(formatCheck):
            self.startSymbol = data[0]
            self.header = data[1]
            self.data = np.array([data[2], data[3], data[4], data[5]])
            self.crc8 = data[6]

    #Checks format of the packet
    def checkMsgFormat(self):
        if(self.startSymbol == 0x55):
            if(self.crc8 == self.getCRC8()):
                return True
        
        return False
    
    #Buffer the received bytes
    def AddRxBytesRoBuffer(self, rxData, rxLength):
        for i in range(rxLength):
            global rx_data_buff
            rx_data_buff = np.roll(rx_data_buff,1)
            rx_data_buff[0] = rxData[rxLength-(i+1)]
            if(self.checkRawMsgFormat( rx_data_buff)):
                #Data good - process
                self.buildStructureFromRxData(rx_data_buff)
                return True
        return False
    
