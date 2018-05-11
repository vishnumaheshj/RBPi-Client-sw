from switchboard import *
import json
import serverDB

messageList = {}
messageNum = 0
dev_ready_ntf_capture = None


def prepareBoardInfoReq(nodeid):
    Msg = {'message_type': SB_BOARD_INFO_REQ}
    Msg['node'] = nodeid
    Msg['flags'] = 0
    return Msg


def prepareStateChangeReq(nodeid, sbtype, self):
    Msg = {'message_type': SB_STATE_CHANGE_REQ}
    Msg['node'] = nodeid
    if(sbtype == SB_TYPE_4X4):
        switch1 = self.get_argument('switch1', default=None)
        switch2 = self.get_argument('switch2', default=None)
        switch3 = self.get_argument('switch3', default=None)
        switch4 = self.get_argument('switch4', default=None)
        Msg['sbType'] = SB_TYPE_4X4
        Msg['switch1'] = SW_TURN_ON if (switch1 == 'on') else SW_TURN_OFF
        Msg['switch2'] = SW_TURN_ON if (switch2 == 'on') else SW_TURN_OFF
        Msg['switch3'] = SW_TURN_ON if (switch3 == 'on') else SW_TURN_OFF
        Msg['switch4'] = SW_TURN_ON if (switch4 == 'on') else SW_TURN_OFF
        Msg['switch5'] = SW_DONT_CARE
        Msg['switch6'] = SW_DONT_CARE
        Msg['switch7'] = SW_DONT_CARE
        Msg['switch8'] = SW_DONT_CARE
        Msg['mid']     = 0 #For now no request completion lookup. 
    return Msg

def processMsgFromClient(connection, remote_server, Message):
    clientMessage = json.loads(Message)
    if clientMessage['message_type'] == SB_BOARD_INFO_RSP:
        print ("Info Response received")
        serverDB.updateNode(clientMessage)
    elif clientMessage['message_type'] == SB_STATE_CHANGE_RSP:
        print ("State change Response received")
        connection.write_message(msg)
    elif clientMessage['message_type'] == SB_DEVICE_READY_NTF:
        global dev_ready_ntf_capture
        dev_ready_ntf_capture = Message
        print ("Hub is up and running")
        print("Message received %s\n" %clientMessage)
        serverDB.devClientConnection = connection
        '''
        TODO : Device ready should be sent from local-server itself with ip, probably
        '''
    elif clientMessage['message_type'] == SB_DEVICE_INFO_NTF:
        print("hub addr:%s" % format(clientMessage['hubAddr'], '#010x'))
        serverDB.addHubStates(clientMessage)

    if remote_server is not None:
        remote_server.write_message(Message)

def generateHubState():
    # TODO: handle multiple nodes
    hubStates = serverDB.hubStates
    global dev_ready_ntf_capture
    if hubStates is not None:
        msg = {'message_type':SB_DEVICE_INFO_NTF}
        msg['devIndex']     = hubStates['board1']['devIndex']
        msg['sbType']       = hubStates['board1']['type']
        msg['hubAddr']      = json.loads(dev_ready_ntf_capture)['hubAddr']
        msg['epStatus']     = hubStates['board1']['epStatus']
        msg['switch1']      = hubStates['board1']['switch1']
        msg['switch2']      = hubStates['board1']['switch2']
        msg['switch3']      = hubStates['board1']['switch3']
        msg['switch4']      = hubStates['board1']['switch4']
        msg['switch5']      = hubStates['board1']['switch5']
        msg['switch6']      = hubStates['board1']['switch6']
        msg['switch7']      = hubStates['board1']['switch7']
        msg['switch8']      = hubStates['board1']['switch8']
        return msg
    else:
        return None
