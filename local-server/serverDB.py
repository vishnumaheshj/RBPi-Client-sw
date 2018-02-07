from pymongo import MongoClient
from datetime import datetime
from switchboard import *
from bidict import bidict
import os

hubCollection = None
hubStates = None
hubUsers = None
connectionList = bidict()
socketList = dict()
appSocketList = dict()
sessionList = dict()


def initDatabase():
    global hubCollection
    global hubStates
    global hubUsers
    global validHubs

    client = MongoClient()

    db = client.dotslash
    hubCollection = db.hubs
    hubStates = db.hubStates
    hubUsers = db.hubUsers
    validHubs = db.validHubs
    #hubCollection.drop()
    #hubStates.drop()
    #hubUsers.drop()

    print("Database init success")
    print ("hubCollection entries:%d" % hubCollection.count())
    print ("hubStates entries:%d" % hubStates.count())
    print ("hubUsers entries:%d" % hubUsers.count())


def addHub(connection, clientMessage):
    global hubCollection
    global connectionList

    if clientMessage['message_type'] != SB_DEVICE_READY_NTF:
        return 1

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
                "user"         : None,
            }
        )
        print ("Hub Activated.User not registered yet")

    else:
        hubCursor = hubCollection.find_one({"hubAddr": clientMessage['hubAddr'], "$or": [{"active": HS_ONLINE}, {"active": HS_OFFLINE}]})
        if hubCursor is None:
            print("Hub is already registered by user.Activating...") 
            hubCollection.update_one({"hubAddr": clientMessage['hubAddr']},
                                     {"$set":   {
                                                   "joinTime"     : datetime.now(),
                                                   "active"       : HS_ONLINE,
                                                   "offlineSince" : 0,
                                                }
                                     })
        else:
            hubCollection.update_one({"hubAddr": clientMessage['hubAddr']},
                                     {"$set":   {
                                                    "joinTime"     : datetime.now(),
                                                    "active"       : HS_ONLINE,
                                                    "offlineSince" : 0,
                                                }
                                     })
            print("Hub is now marked as active")
    
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
            hubStates.update_one({"hubAddr": cursor['hubAddr']},
                {"$set": {
                            "totalNodes" : cursor['totalNodes'] + 1,
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
            hubStates.update_one({"hubAddr": cursor['hubAddr'],boardStr+".devIndex": clientMessage['devIndex']},
                {"$set": {
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

    document = hubStates.find_one({"hubAddr": clientMessage['hubAddr']})
    if document is not None:
        print("document")
        print(document)


def updateNode(connection, clientMessage):
    global hubStates
    global connectionList

    hubAddr = connectionList.inv[connection]
    boardStr = "board"+str(clientMessage['devIndex'])
    nodeCursor =  hubStates.find_one({"hubAddr": hubAddr, boardStr+".devIndex": clientMessage['devIndex']})

    if nodeCursor is None:
        print("The node to be updated is not present")
    else:
        hubStates.update_one({"hubAddr": nodeCursor['hubAddr']},
            {"$set": {
                        boardStr+".lastModified" : datetime.now(),
                        boardStr+".switch1" : clientMessage['switch1'],
                        boardStr+".switch2" : clientMessage['switch2'],
                        boardStr+".switch3" : clientMessage['switch3'],
                        boardStr+".switch4" : clientMessage['switch4'],
                        boardStr+".switch5" : clientMessage['switch5'],
                        boardStr+".switch6" : clientMessage['switch6'],
                        boardStr+".switch7" : clientMessage['switch7'],
                        boardStr+".switch8" : clientMessage['switch8'],
                    }
            })


def findNode(hubAddr, nodeid):
    boardStr = "board"+str(nodeid)
    row = hubStates.find_one({"hubAddr": hubAddr, boardStr+".devIndex": nodeid})
    if row is not None:
            node = row[boardStr]
            return node
    else:
            return None


def findHub(hubAddr):
    return hubStates.find_one({"hubAddr": hubAddr})


def makeHubOffline(hubAddr):
        hubCollection.update_one({"hubAddr": hubAddr},
            {"$set": {
                "active"       : HS_OFFLINE,
                "offlineSince" : datetime.now(),
                    }
            })

        document = hubCollection.find_one({"hubAddr": hubAddr})
        if document is not None:
            print("document")
            print(document)
            print("'''''''''''''''")


def addUser(username, password):
    cursor = hubUsers.find_one({"username": username})
    if cursor is None:
        print("New user..")
        phash = security.hashInterface.hash(password)
        hubUsers.insert_one(
            {
                "username": username,
                "passwordhash" : phash,
            }
        )
        status = None
    else:
        print("Already registered user!")
        status = "Already registered user!"

    userDB = hubUsers.find_one({})
    if userDB is not None:
        print("user database")
        print(userDB)

    return status


def loginUser(username, password):
    cursor = hubUsers.find_one({"username": username})
    if cursor is not None:
        print("checking hash")
        hashStatus = security.hashInterface.verify(password, cursor['passwordhash'])
        if hashStatus is True:
            print("user loged in: %s" % username)
            hubUsers.update_one({"username": username},
                                         {"$set": {
                                             "loggedin": 1,
                                             "lastlogin": datetime.now()
                                         }
                                         })
            status = None
        else:
            status = "Username/Password mismatch"
            print("login attempt failed: password is incorrect")
    else:
        status = "Username/Password mismatch"
        print("login attempt failed: No such user")

    userDB = hubUsers.find_one({})
    if userDB is not None:
        print("user database")
        print(userDB)

    return status


def logoutUser(username):
    cursor = hubUsers.find_one({"username": username})
    if cursor is not None:
        hubUsers.update_one({"username": username},
                             {"$set": {
                                        "loggedin"  : 0,
                                      }
                             })
        status = None
        print("user %s logged out" % username)
    else:
        print("unknown user!")
        status = "unknown user!"

    userDB = hubUsers.find_one({})
    if userDB is not None:
        print("user database")
        print(userDB)

    return status

def checkHubValid(hubId):
    global validHubs
    cursor = validHubs.find_one({"hubAddr": hubId})
    if cursor is None:
            status = "Hub ID is not valid"
    else:
            status = None
    return status


def registerHub(username, hubId):
    cursor = hubUsers.find_one({"username": username})
    if cursor is not None:
        hubCursor = hubCollection.find_one({"hubAddr": hubId})
        if hubCursor is not None:
            hubCollection.update_one({"hubAddr": hubId},
                                     {"$set":   {
                                                    "user": username,
                                                }
                                     })
            status = None
        else:
            print("User Added.Hub hasn't joined")
            hubCollection.insert_one(
                {
                "hubAddr"      : hubId,
                "joinTime"     : None,
                "active"       : None,
                "offlineSince" : None,
                "user"         : username,
                }
            )
 
            status = None
    else:
        print("Signup failed.Hub not registered")
        status = "Signup failed.Hub not registered"

    hubsDB = hubCollection.find_one({})
    if hubsDB is not None:
        print("hub database")
        print(hubsDB)

    return status


def findUserHub(username):
    cursor = hubUsers.find_one({"username": username})
    if cursor is not None:
        hubCursor = hubCollection.find_one({"user": username})
        if hubCursor is not None:                               # Assuming a single document for now.
            return hubCursor["hubAddr"]
        else:
            return 0
    else:
        return 0

def checkHubActive(hubAddr):
    cursor = hubCollection.find_one({"hubAddr": hubAddr})
    if cursor and "active" in cursor:
            if (cursor["active"] == HS_ONLINE):
                    return True
            else:
                    return False
    else:
            return False
