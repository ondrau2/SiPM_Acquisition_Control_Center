import numpy as np
import Communication_lib.SerialMessage as SerialMessage
from dataclasses import dataclass

###############################################################################
#################################----VARIABLES-----############################
DAC_CH_A_ID = 1
DAC_CH_B_ID = 2
DAC_CH_C_ID = 3

aliveCntr = 0

###############################################################################
#######################----CLASSES AND FUNCTIONS-----##########################

##Status variables
@dataclass
class CTRL_MSG:
    boardAlive = False
    DAC_A_val = 0
    DAC_B_val = 0
    DAC_C_val = 0
    measRunning = False
    processingType = 0

##Handles the board alive variable
def boardAliveWDG():
    global aliveCntr 
    aliveCntr = aliveCntr + 1
    if(aliveCntr > 3):
        CTRL_MSG.boardAlive = False
    else: 
        CTRL_MSG.boardAlive = True

##Handle heartbeat reception
def HB_handle(measStatus):
    global aliveCntr 
    aliveCntr = 0
    CTRL_MSG.measRunning = bool(measStatus)

##Handle all control messages (non-acqiosition) 
def handle_Rx_CTRL_Msg(header, data):
    #Heartbeat
    if(header == SerialMessage.RxMsgID.heart_beat.value):
        HB_handle(data[3])

    #Measurement start
    elif(header == SerialMessage.RxMsgID.meas_start_ack.value):
        CTRL_MSG.measRunning = True

    #Measurement stop
    elif(header == SerialMessage.RxMsgID.meas_stop_ack.value):
        CTRL_MSG.measRunning = False

    #DAC value set response
    elif(header == SerialMessage.RxMsgID.DAC_set_resp.value):
        if(data[2]==DAC_CH_A_ID):
            CTRL_MSG.DAC_A_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 
        elif(data[2]==DAC_CH_B_ID):
            CTRL_MSG.DAC_B_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 
        elif(data[2]==DAC_CH_C_ID):
            CTRL_MSG.DAC_C_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 

    #Processing type changes response
    elif(header == SerialMessage.RxMsgID.proc_type_ack.value):
        CTRL_MSG.processingType = data[0]


##Class with functions for control command packet build
class CmdRespBuild:  

    #Build the DAC voltage request ctrl message
    def build_DAC_set_request(ch_num, value):
        msg = SerialMessage.SerialMessage()
    
        msg.startSymbol = 0x55
    
        if(ch_num == 1):
            msg.header = SerialMessage.TxMsgID.DAC_A_set
        elif(ch_num == 2):
            msg.header = SerialMessage.TxMsgID.DAC_B_set
        elif(ch_num == 3):
            msg.header = SerialMessage.TxMsgID.DAC_C_set
    
        dec_val = np.round(np.double(value)*1000)
        msg.data[0] = np.uint8(np.bitwise_and(np.uint32(dec_val), 0xFF))
        msg.data[1] = np.uint8(np.bitwise_and(np.uint32(dec_val) >> 8, 0xFF))
    
        msg.getCRC8()
    
        return msg.buildByteArr()
    
    #Build measurement start/stop array
    def MeasurementStart_Stop():
        msg = SerialMessage.SerialMessage()
    
        msg.startSymbol = 0x55
    
        if(CTRL_MSG.measRunning == False):
            msg.header = SerialMessage.TxMsgID.meas_start_req
        else:
            msg.header = SerialMessage.TxMsgID.meas_stop_req
    
        msg.getCRC8()
    
        return msg.buildByteArr()
    
    #Build processing type change array
    def build_processing_type_request(type):
        msg = SerialMessage.SerialMessage()
    
        msg.startSymbol = 0x55
    
        msg.header = SerialMessage.TxMsgID.processing_type
    
        if(type == 'raw_TOT'):
            msg.data[0] = SerialMessage.PulseProcesssingTypes.raw_TOT.value
        elif(type == 'exponential_fit'):
            msg.data[0] = SerialMessage.PulseProcesssingTypes.exponential_fit.value
        elif(type == '[NA] linear_fit'):
            msg.data[0] = SerialMessage.PulseProcesssingTypes.linear_fit.value
        elif(type == '[NA] NN'):
            msg.data[0] = SerialMessage.PulseProcesssingTypes.NN.value
    
        msg.getCRC8()
    
        return msg.buildByteArr()