from switchboard import *
import json
import serverDB

messageList = {}
messageNum = 0


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

