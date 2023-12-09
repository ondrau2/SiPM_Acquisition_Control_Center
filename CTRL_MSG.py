import numpy as np
import SerialMessage
from dataclasses import dataclass

DAC_CH_A_ID = 1
DAC_CH_B_ID = 2
DAC_CH_C_ID = 3

@dataclass
class CTRL_MSG:
    boardAlive = False
    DAC_A_val = 0
    DAC_B_val = 0
    DAC_C_val = 0
    measRunning = False
    processingType = 0

aliveCntr = 0

def boardAliveWDG():
    global aliveCntr 
    aliveCntr = aliveCntr + 1
    if(aliveCntr > 3):
        CTRL_MSG.boardAlive = False
    else: 
        CTRL_MSG.boardAlive = True
def HB_handle(measStatus):
    global aliveCntr 
    aliveCntr = 0
    CTRL_MSG.measRunning = bool(measStatus)

def handle_Rx_CTRL_Msg(header, data):
    #HB
    if(header == SerialMessage.RxMsgID.heart_beat.value):
        HB_handle(data[3])

    if(header == SerialMessage.RxMsgID.meas_start_ack.value):
        CTRL_MSG.measRunning = True

    if(header == SerialMessage.RxMsgID.meas_stop_ack.value):
        CTRL_MSG.measRunning = False

    if(header == SerialMessage.RxMsgID.DAC_set_resp.value):
        if(data[2]==DAC_CH_A_ID):
            CTRL_MSG.DAC_A_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 
        elif(data[2]==DAC_CH_B_ID):
            CTRL_MSG.DAC_B_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 
        elif(data[2]==DAC_CH_C_ID):
            CTRL_MSG.DAC_C_val = (np.uint8(data[1]) << 8 ) | np.uint8(data[0]) 
    if(header == SerialMessage.RxMsgID.proc_type_ack.value):
        CTRL_MSG.processingType = data(0)

    
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

def MeasurementStart_Stop():
    msg = SerialMessage.SerialMessage()

    msg.startSymbol = 0x55

    if(CTRL_MSG.measRunning == False):
        msg.header = SerialMessage.TxMsgID.meas_start_req
    else:
        msg.header = SerialMessage.TxMsgID.meas_stop_req

    msg.getCRC8()

    return msg.buildByteArr()