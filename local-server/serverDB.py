from datetime import datetime
from switchboard import *
from bidict import bidict
import os

hubStates = None
hubUsers = None
devClientConnection = None


def initDatabase():
    global hubStates
    global hubUsers
    print(" init success")

def addHubStates(clientMessage):
    global hubStates
    hubStates = {}
    hubStates['totalNodes'] = 1
    boardStr = "board"+str(clientMessage['devIndex'])
    hubStates[boardStr]  = {}
    hubStates[boardStr]['devIndex']     = clientMessage['devIndex']
    hubStates[boardStr]['type']         = clientMessage['sbType']
    hubStates[boardStr]['epStatus']     = clientMessage['epStatus']
    hubStates[boardStr]['lastModified'] = datetime.now()
    hubStates[boardStr]['switch1']      = clientMessage['switch1']
    hubStates[boardStr]['switch2']      = clientMessage['switch2']
    hubStates[boardStr]['switch3']      = clientMessage['switch3']
    hubStates[boardStr]['switch4']      = clientMessage['switch4']
    hubStates[boardStr]['switch5']      = clientMessage['switch5']
    hubStates[boardStr]['switch6']      = clientMessage['switch6']
    hubStates[boardStr]['switch7']      = clientMessage['switch7']
    hubStates[boardStr]['switch8']      = clientMessage['switch8']

def updateNode(clientMessage):
    global hubStates
    boardStr = "board"+str(clientMessage['devIndex'])

    if boardStr in hubStates:
        hubStates[boardStr]['lastModified'] = datetime.now()
        hubStates[boardStr]['switch1']      = clientMessage['switch1']
        hubStates[boardStr]['switch2']      = clientMessage['switch2']
        hubStates[boardStr]['switch3']      = clientMessage['switch3']
        hubStates[boardStr]['switch4']      = clientMessage['switch4']
        hubStates[boardStr]['switch5']      = clientMessage['switch5']
        hubStates[boardStr]['switch6']      = clientMessage['switch6']
        hubStates[boardStr]['switch7']      = clientMessage['switch7']
        hubStates[boardStr]['switch8']      = clientMessage['switch8']
    else:
        print("The node to be updated is not present")

def getHubState():
    global hubStates
    return hubStates

def findNode(nodeid):
    boardStr = "board"+str(nodeid)
    row = hubStates.find_one({boardStr+".devIndex": nodeid})
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
