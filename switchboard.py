import ctypes
from ctypes import *

SB_BOARD_INFO_REQ   = 0x01
SB_BOARD_INFO_RSP   = 0x02
SB_STATE_CHANGE_REQ = 0x03
SB_STATE_CHANGE_RSP = 0x04

SB_DEVICE_READY_NTF = 0x05
SB_DEVICE_READY_REQ = 0x06

SB_DEVICE_TYPE_REQ  = 0x07
SB_DEVICE_TYPE_NTF  = 0x08
SB_DEVICE_INFO_NTF  = 0x09

class sbMessageHdr_t(Structure):
    _fields_ = [("type", c_ubyte),
                ("mid", c_ubyte),
                ("nodeid",c_ubyte)]

# Switch Board Types
SB_TYPE_PLUG  = 0x01
SB_TYPE_4X4   = 0x02

class switchBoardType_t(Structure):
    _fields_ = [("type", c_ubyte)]

# Switch state change request defines
SW_TURN_OFF  = 0x0
SW_TURN_ON   = 0x1
SW_KEEP_OFF  = 0x2
SW_KEEP_ON   = 0x3
SW_DONT_CARE = 0x4

# Switch state change reply defines
SW_STATEC_SUCCESS        = 0x1
SW_STATEC_FAILED         = 0x2
SW_STATEC_NOT_IN_USE     = 0x3
SW_STATEC_NOT_WORKING    = 0x4
SW_STATEC_DONT_CARE      = 0x5

class stateData(Structure):
    _fields_ = [("switch1", c_ubyte, 4),
                ("switch2", c_ubyte, 4),
                ("switch3", c_ubyte, 4),
                ("switch4", c_ubyte, 4),
                ("switch5", c_ubyte, 4),
                ("switch6", c_ubyte, 4),
                ("switch7", c_ubyte, 4),
                ("switch8", c_ubyte, 4)]

class switchState_t(Structure):
    _fields_ = [("state", stateData)]

# Switch states
SW_OFF           = 0x00
SW_ON            = 0x01
SW_NOT_IN_USE    = 0x02
SW_NOT_WORKING   = 0x03
SW_NOT_PRESENT   = 0x04
SW_UNKNOWN       = 0x05

class hwSwitchBoardState_t(Structure):
    _fields_ = [("switch1", c_ubyte),
                ("switch2", c_ubyte),
                ("switch3", c_ubyte),
                ("switch4", c_ubyte),
                ("switch5", c_ubyte),
                ("switch6", c_ubyte),
                ("switch7", c_ubyte),
                ("switch8", c_ubyte)]

class sBoard_t(Structure):
    _fields_ = [("sbType", switchBoardType_t),
                ("switchData", switchState_t)]

class sInfoReq_t(Structure):
    _fields_ = [("flags", c_ubyte)]

class sInfoRsp_t(Structure):
    _fields_ = [("sbType", switchBoardType_t),
                ("currentState", hwSwitchBoardState_t)]

# Device join states
DJ_NEW_DEVICE     = 0x01
DJ_KNOWN_DEVICE   = 0x02

# Node States
NS_JUST_JOINED          = 0x1
NS_EP_ACTIVE            = 0x2
NS_EP_PARENT_REACHED    = 0x3
NS_NOT_REACHABLE        = 0x4
NS_BOARD_READY          = 0x5

# Hub States
HS_ONLINE     = 0x1
HS_OFFLINE    = 0x2

class sDevInfo_t(Structure):
    _fields_ = [("joinState", c_ubyte),
                ("sbType", switchBoardType_t),
                ("devIndex", c_ubyte),
                ("ieeeAddr", c_ulonglong),
                ("epStatus", c_ubyte),
                ("currentState", hwSwitchBoardState_t)]

class sbMessageData_t(Union):
    _fields_ = [("boardData", sBoard_t),
                ("infoReqData", sInfoReq_t),
                ("infoRspData", sInfoRsp_t),
                ("devInfo", sDevInfo_t)]

class sbMessage_t(Structure):
    _fields_ = [("hdr", sbMessageHdr_t),
                ("data", sbMessageData_t)]
