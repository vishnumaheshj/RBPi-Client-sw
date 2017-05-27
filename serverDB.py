from pymongo import MongoClient
from datetime import datetime
from switchboard import *
import pickle

hubCollection = None
hubStates = None
connectionList = {}

def initDatabase():
    global hubCollection
    global hubStates

    client = MongoClient()
    db = client.dotslash
    hubCollection = db.hubs
    hubStates = db.hubStates

    # Debug
    print("Database init success")
    print ("hubCollection entries:%d" % hubCollection.count())
    print ("hubStates entries:%d" % hubStates.count())


def addHub(connection, clientMessage):
    global hubCollection

    if clientMessage['message_type'] != SB_DEVICE_READY_NTF:
        return 1

    #connectionList[str(clientMessage['hubAddr'])] = connection
    connectionList[connection] = clientMessage['hubAddr']
    
    cursor = hubCollection.find_one({"hubAddr": clientMessage['hubAddr']})
    if cursor is None:
        print ("cursor none, adding Hub")
        hubCollection.insert_one(
            {
                "hubAddr"      : clientMessage['hubAddr'],
                "joinTime"     : datetime.now(),
                "active"       : HS_ONLINE,
                "offlineSince" : 0,
            }
        )
        print ("Hub Added")

    else:
        print ("Known hub")
    cursor = hubCollection.find({"hubAddr": clientMessage['hubAddr']})
    for document in cursor:
        print (document)
    print("###############################################################")
    print("connection lisr")
    print(connectionList)

def addHubStates(clientMessage):
    #{"switch6": 4, "joinState": 2, "message_type": 9, "devIndex": 1, "ieeeAddr": 5149013057361641, "switch2": 0, "switch4": 0, "switch7": 4, "epStatus": 5, "sbType": 2, "switch1": 1, "switch3": 1, "switch5": 4, "switch8": 4}
    
    global hubStates

    if clientMessage['message_type'] != SB_DEVICE_INFO_NTF:
        return 1

    print("Hub Info message")    
    cursor = hubStates.find_one({"hubAddr": clientMessage['hubAddr']})
    boardStr = "board"+str(clientMessage['devIndex'])
    if cursor is None:
        print ("cursor none, adding Hub State")
        hubStates.insert_one(
		{
            "hubAddr"     : clientMessage['hubAddr'],
            "totalNodes"  : 1,
            boardStr      : {
                                "devIndex"     : clientMessage['devIndex'],
                                "type"         : clientMessage['sbType'],
                                "epStatus"     : clientMessage['epStatus'],
                                "lastModified" : datetime.now(),
                                "switch1"      : clientMessage['switch1'],
                                "switch2"      : clientMessage['switch2'],
                                "switch3"      : clientMessage['switch3'],
                                "switch4"      : clientMessage['switch4'],
                                "switch5"      : clientMessage['switch5'],
                                "switch6"      : clientMessage['switch6'],
                                "switch7"      : clientMessage['switch7'],
                                "switch8"      : clientMessage['switch8'],
                            }
        })
    else:
        print("state present, updating Hub State")
        boardStr = "board"+str(clientMessage['devIndex'])
        nodeCursor =  hubStates.find_one({boardStr+".devIndex": clientMessage['devIndex']})
        if nodeCursor is None:
            print("New Node Joined");
            hubStates.update_one({"hubAddr", cursor.hubAddr},
                {"$set": {
                            "totalNodes" : cursor.totalNodes + 1,
                            boardStr     : {
                                            "devIndex"     : clientMessage['devIndex'],
                                            "type"         : clientMessage['sbType'],
                                            "epStatus"     : clientMessage['epStatus'],
                                            "lastModified" : datetime.now(),
                                            "switch1"      : clientMessage['switch1'],
                                            "switch2"      : clientMessage['switch2'],
                                            "switch3"      : clientMessage['switch3'],
                                            "switch4"      : clientMessage['switch4'],
                                            "switch5"      : clientMessage['switch5'],
                                            "switch6"      : clientMessage['switch6'],
                                            "switch7"      : clientMessage['switch7'],
                                            "switch8"      : clientMessage['switch8'],
                                            }
                         }
                }
            )
        else:
                print("multiple hub info message of same node")
                pass

    document = hubStates.find_one({"hubAddr": clientMessage['hubAddr']})
    if document is not None:
            print(document)








