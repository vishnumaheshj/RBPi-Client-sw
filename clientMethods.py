import switchboard
from switchboard import *
import ctypes

readId  =  int()
writeId = int()
listenThreadEvent = 0

lib = ctypes.cdll.LoadLibrary("/home/pi/dotslash/client/libshm.so")

def writeShm(message):
    lib.write_shm(byref(message), writeId)

def readShm(message):
    lib.read_shm(byref(message), readId)

def createMessageForHub(Msg):
    if Msg['message_type'] == SB_BOARD_INFO_REQ:
        print ("Info Req")
        HubReq = sbMessage_t()
        HubReq.hdr.type = SB_BOARD_INFO_REQ
        HubReq.hdr.nodeid = int(Msg['node'])
        HubReq.data.infoReqData.flags = 0
        return HubReq
    elif Msg['message_type'] == SB_STATE_CHANGE_REQ:
        print ("State Change Req")
        HubReq = sbMessage_t()
        HubReq.hdr.type = SB_STATE_CHANGE_REQ
        HubReq.hdr.nodeid = int(Msg['node'])
        HubReq.hdr.mid = int(Msg['mid'])
        if (int(Msg['sbType']) == SB_TYPE_4X4):
            HubReq.data.boardData.sbType.type = SB_TYPE_4X4
            HubReq.data.boardData.switchData.state.switch1 = int(Msg['switch1'])
            HubReq.data.boardData.switchData.state.switch2 = int(Msg['switch2'])
            HubReq.data.boardData.switchData.state.switch3 = int(Msg['switch3'])
            HubReq.data.boardData.switchData.state.switch4 = int(Msg['switch4'])
            HubReq.data.boardData.switchData.state.switch5 = SW_DONT_CARE
            HubReq.data.boardData.switchData.state.switch6 = SW_DONT_CARE
            HubReq.data.boardData.switchData.state.switch7 = SW_DONT_CARE
            HubReq.data.boardData.switchData.state.switch8 = SW_DONT_CARE
        else:
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

def createMessageForServer(Msg):
    if Msg.hdr.type == SB_BOARD_INFO_RSP:
        print("Info Rsp")
        SerReq = {'message_type': SB_BOARD_INFO_RSP}
        SerReq['devIndex'] = Msg.hdr.nodeid
        SerReq['mid'] = Msg.hdr.mid
        SerReq['sbType']  = Msg.data.infoRspData.sbType.type
        SerReq['switch1'] = Msg.data.infoRspData.currentState.switch1
        SerReq['switch2'] = Msg.data.infoRspData.currentState.switch2
        SerReq['switch3'] = Msg.data.infoRspData.currentState.switch3
        SerReq['switch4'] = Msg.data.infoRspData.currentState.switch4
        SerReq['switch5'] = Msg.data.infoRspData.currentState.switch5
        SerReq['switch6'] = Msg.data.infoRspData.currentState.switch6
        SerReq['switch7'] = Msg.data.infoRspData.currentState.switch7
        SerReq['switch8'] = Msg.data.infoRspData.currentState.switch8
        return SerReq
    elif Msg.hdr.type == SB_STATE_CHANGE_RSP:
        print ("State Change Rsp")
        SerReq = {'message_type': SB_STATE_CHANGE_RSP}
        SerReq['devIndex'] = Msg.hdr.nodeid
        SerReq['sbType']  = Msg.data.infoRspData.sbType.type
        SerReq['switch1'] = Msg.data.boardData.switchData.state.switch1
        SerReq['switch2'] = Msg.data.boardData.switchData.state.switch2
        SerReq['switch3'] = Msg.data.boardData.switchData.state.switch3
        SerReq['switch4'] = Msg.data.boardData.switchData.state.switch4
        SerReq['switch5'] = Msg.data.boardData.switchData.state.switch5
        SerReq['switch6'] = Msg.data.boardData.switchData.state.switch6
        SerReq['switch7'] = Msg.data.boardData.switchData.state.switch7
        SerReq['switch8'] = Msg.data.boardData.switchData.state.switch8
        return SerReq
    elif Msg.hdr.type == SB_DEVICE_READY_NTF:
        print("Device Up notification")
        SerReq = {'message_type': SB_DEVICE_READY_NTF}
        SerReq['hubAddr'] = 0x0102030405060708
        return SerReq
    elif Msg.hdr.type == SB_DEVICE_INFO_NTF:
        print("Device Info notification")
        print("PYTHON:::size of msg:%i" % sizeof(sbMessage_t))
        SerReq = {'message_type': SB_DEVICE_INFO_NTF}
        SerReq['joinState'] = Msg.data.devInfo.joinState
        SerReq['sbType']    = Msg.data.devInfo.sbType.type
        SerReq['devIndex']  = Msg.data.devInfo.devIndex
        SerReq['hubAddr']   = 0x0102030405060708
        SerReq['epStatus']  = Msg.data.devInfo.epStatus
        SerReq['switch1']   = Msg.data.devInfo.currentState.switch1
        SerReq['switch2']   = Msg.data.devInfo.currentState.switch2
        SerReq['switch3']   = Msg.data.devInfo.currentState.switch3
        SerReq['switch4']   = Msg.data.devInfo.currentState.switch4
        SerReq['switch5']   = Msg.data.devInfo.currentState.switch5
        SerReq['switch6']   = Msg.data.devInfo.currentState.switch6
        SerReq['switch7']   = Msg.data.devInfo.currentState.switch7
        SerReq['switch8']   = Msg.data.devInfo.currentState.switch8
        return SerReq
    else:
        print("Unknown message")
        return {}


def initializeHub():
    global readId
    global writeId
    global listenThreadEvent
    readId = lib.init_read_shm()
    writeId = lib.init_write_shm()
    inMsg = sbMessage_t()

    readShm(inMsg)

    if (inMsg.hdr.type == SB_DEVICE_READY_NTF):
        listenThreadEvent = None
        return createMessageForServer(inMsg)
    else:
        listenThreadEvent = SB_DEVICE_READY_REQ


def sendDeviceReq(req):
    inMsg = sbMessage_t()
    inMsg.hdr.type = req
    writeShm(inMsg)

def checkInit():
    while(listenThreadEvent == 0):
        continue
    if listenThreadEvent == SB_DEVICE_READY_REQ:
        sendDeviceReq(SB_DEVICE_READY_REQ)
