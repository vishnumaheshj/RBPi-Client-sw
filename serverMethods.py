import switchboard
from switchboard import *
import json

global_devlist = []
global_num_devices = 0

class dotslash_hub:
    def __init__(self,a,b):
        self.id = a
        self.conn = b
        self.nodes = []

class switch_node:
    def __init__(self, id, type, a, b, c, d):
        self.id = id
        self.type = type
        self.switch1 = a
        self.switch2 = b
        self.switch3 = c
        self.switch4 = d
        


def sentBoardInfoReq(nodeid):
    Msg = {'message_type': SB_BOARD_INFO_REQ}
    Msg['node'] = nodeid
    Msg['flags'] = 0
    return Msg

def sentStateChangeReq(nodeid):
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['node'] = nodeid
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
        print ("Info Response received")
        for device in global_devlist:
            if(device.conn == connection):
                id = clientMessage['devIndex'] - 1
                device.nodes[id].switch1 = clientMessage['switch1']
                device.nodes[id].switch2 = clientMessage['switch2']
                device.nodes[id].switch3 = clientMessage['switch3']
                device.nodes[id].switch4 = clientMessage['switch4']
    elif clientMessage['message_type'] == SB_STATE_CHANGE_RSP:
        print ("State change Response received")
    elif clientMessage['message_type'] == SB_DEVICE_READY_NTF:
        print ("Hub is up and running")
        global_num_devices =  1
        if global_num_devices not in [hub.id for hub in global_devlist]:
            device = dotslash_hub(global_num_devices, connection)
            global_devlist.append(device)
        print ("Total Devices %i" % len(global_devlist))
    elif clientMessage['message_type'] == SB_DEVICE_INFO_NTF:
        if clientMessage['sbType'] == SB_TYPE_4X4:
            id = clientMessage['devIndex']
            type = clientMessage['sbType']
            switch1 = clientMessage['switch1']
            switch2 = clientMessage['switch2']
            switch3 = clientMessage['switch3']
            switch4 = clientMessage['switch4']
            node = switch_node(id, type, switch1, switch2, switch3, switch4)
            for device in global_devlist:
                if(device.conn == connection):
                    device.nodes.append(node)
            print("Received node info switch 4*4")
        else:
            print("Received node info unknown device")



