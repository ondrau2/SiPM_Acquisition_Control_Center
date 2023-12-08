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
        pass

    if(header == SerialMessage.RxMsgID.meas_stop_ack.value):
        pass

    if(header == SerialMessage.RxMsgID.DAC_set_resp.value):
        if(data[2]==DAC_CH_A_ID):
            CTRL_MSG.DAC_A_val = int.from_bytes(np.array([data(1), data(0)], byteorder = 'little'))
        elif(data[2]==DAC_CH_B_ID):
            CTRL_MSG.DAC_B_val = int.from_bytes(np.array([data(1), data(0)], byteorder = 'little'))
        elif(data[2]==DAC_CH_C_ID):
            CTRL_MSG.DAC_C_val = int.from_bytes(np.array([data(1), data(0)], byteorder = 'little'))
    if(header == SerialMessage.RxMsgID.proc_type_ack.value):
        CTRL_MSG.processingType = data(0)

    
