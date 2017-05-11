import switchboard
from switchboard import *

def createMessageForHub(Msg):
    if Msg['message_type'] == SB_BOARD_INFO_REQ:
        print ("Info Req")
        HubReq = sbMessage_t()
        HubReq.hdr.type = SB_BOARD_INFO_REQ
        HubReq.data.infoReqData.flags = 0
        return HubReq
    elif Msg['message_type'] == SB_STATE_CHANGE_REQ:
        print ("State Change Req")
        HubReq = sbMessage_t()
        HubReq.hdr.type = SB_STATE_CHANGE_REQ
        HubReq.data.boardData.sbType.type = SB_TYPE_4X4
        HubReq.data.boardData.switchData.state.switch1 = SW_TURN_ON
        HubReq.data.boardData.switchData.state.switch2 = SW_TURN_OFF
        HubReq.data.boardData.switchData.state.switch3 = SW_TURN_ON
        HubReq.data.boardData.switchData.state.switch4 = SW_TURN_OFF
        HubReq.data.boardData.switchData.state.switch5 = SW_DONT_CARE
        HubReq.data.boardData.switchData.state.switch6 = SW_DONT_CARE
        HubReq.data.boardData.switchData.state.switch7 = SW_DONT_CARE
        HubReq.data.boardData.switchData.state.switch8 = SW_DONT_CARE
        return HubReq
