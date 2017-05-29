from pymongo import MongoClient
from datetime import datetime
from switchboard import *
from bidict import bidict 

hubCollection = None
hubStates = None
connectionList = bidict()

def initDatabase():
    global hubCollection
    global hubStates

    client = MongoClient()
    db = client.dotslash
    hubCollection = db.hubs
    hubStates = db.hubStates

    # REMOVE
    hubCollection.drop()
    hubStates.drop()
    # Debug
    print("Database init success")
    print ("hubCollection entries:%d" % hubCollection.count())
    print ("hubStates entries:%d" % hubStates.count())


def addHub(connection, clientMessage):
    global hubCollection
    global connectionList

    if clientMessage['message_type'] != SB_DEVICE_READY_NTF:
        return 1

    #connectionList(connection) = clientMessage['hubAddr']
    connectionList[clientMessage['hubAddr']] = connection
    
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
    print("connection list")
    print(connectionList)
    print("###############################################################")

def addHubStates(clientMessage, connection):
    
    global hubStates
    global connectionList

    print("Hub Info message")    
    hubAddr = connectionList.inv[connection]
    cursor = hubStates.find_one({"hubAddr": hubAddr})
    boardStr = "board"+str(clientMessage['devIndex'])
    if cursor is None:
        print ("cursor none, adding Hub State")
        hubStates.insert_one(
        {
            "hubAddr"     : hubAddr,
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
        nodeCursor =  hubStates.find_one({"hubAddr": hubAddr, boardStr+".devIndex": clientMessage['devIndex']})
        if nodeCursor is None:
            print("New Node Joined")
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
        print("document")
        print(document)


def updateNode(connection, clientMessage):
    print("updating database")
    pass






