import switchboard
from switchboard import *
import json
import serverDB

global_devlist = []
global_num_devices = 0

class dotslash_hub:
    def __init__(self,a,b):
        self.id = a
        self.conn = b

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

def processMsgFromClient(connection, clientMessage):
    clientMessage = json.loads(clientMessage)
    if clientMessage['message_type'] == SB_BOARD_INFO_RSP:
        print("Board Infp Rsp")
        serverDB.updateNode(connection, clientMessage)
        print("Message received %s\n" %clientMessage)
    elif clientMessage['message_type'] == SB_STATE_CHANGE_RSP:
        print ("State change Response received")
        print("Message received %s\n" %clientMessage)
    elif clientMessage['message_type'] == SB_DEVICE_READY_NTF:
        print ("Hub is up and running")
        print("Message received %s\n" %clientMessage)
        global_num_devices = 1
        if global_num_devices not in [hub.id for hub in global_devlist]:
            device = dotslash_hub(global_num_devices, connection)
            global_devlist.append(device)
        print ("Total Devices %i" % len(global_devlist))
        clientMessage['hubAddr'] = 0x0102030405060708
        serverDB.addHub(connection, clientMessage)

    elif clientMessage['message_type'] == SB_DEVICE_INFO_NTF:
        print("Hub Info Rsp")
        print("Message received %s\n" %clientMessage)
        print("hub addr:%s" % format(clientMessage['hubAddr'], '#010x'))
        serverDB.addHubStates(clientMessage)

