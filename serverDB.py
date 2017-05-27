from pymongo import MongoClient
from datetime import datetime
from switchboard import *

hubCollection = None
hubStates = None

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


def addHub(clientMessage):
    global hubCollection
    global hubStates

    if clientMessage['message_ready'] == SB_DEVICE_READY_NTF:
        ieeeAddr = clientMessage['ieeeAddr']
    else:
        return 1

    cursor = hubCollection.find({"hubAddr": clientMessage['hubAddr']})
    if cursor is None:
        print "cursor none, adding document"
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

