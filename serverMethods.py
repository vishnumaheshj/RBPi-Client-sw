import switchboard
from switchboard import *

def sentBoardInfoReq():
    Msg = {'message_type': SB_BOARD_INFO_REQ}
    Msg['flags'] = 0
    return Msg

def sentStateChangeReq():
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['sbType'] = SB_TYPE_4X4
    Msg['switch1'] = SW_TURN_ON
    Msg['switch2'] = SW_TURN_OFF
    Msg['switch3'] = SW_TURN_ON
    Msg['switch4'] = SW_TURN_OFF
    Msg['switch5'] = SW_DONT_CARE
    Msg['switch6'] = SW_DONT_CARE
    Msg['switch7'] = SW_DONT_CARE
    Msg['switch8'] = SW_DONT_CARE
    return Msg

