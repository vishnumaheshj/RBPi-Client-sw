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
    global hubStates
    global hubUsers

    dbClient = MongoClient()

    db = dbClient.dotslash
    hubStates = db.hubStates
    hubUsers = db.hubUsers

    #hubStates.drop()
    #hubUsers.drop()

    print("Database init success")
    print ("hubStates entries:%d" % hubStates.count())
    print ("hubUsers entries:%d" % hubUsers.count())


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
