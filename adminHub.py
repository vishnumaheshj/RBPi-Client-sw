from pymongo import MongoClient
import os

#client = MongoClient()
client = MongoClient(os.environ.get('MONGOLAB_URI'),
                      connectTimeoutMS=30000,
                      socketTimeoutMS=None,
                      socketKeepAlive=True)

db = client.dotslash
validHubs = db.validHubs
hubCollection = db.hubs
hubStates = db.hubStates
hubUsers = db.hubUsers

#hubStates.drop()
#hubCollection.drop()
#hubUsers.drop()
#validHubs.drop()


#addr = raw_input("Enter hub addr")
#validHubs.insert_one({"hubAddr": int(addr,16)})
#print ("hubCollection entries:%d" % hubCollection.count())
#print ("hubStates entries:%d" % hubStates.count())
#print ("hubUsers entries:%d" % hubUsers.count())
#print ("validHubs entries:%d" % validHubs.count())
#
for document in validHubs.find():
    print (document)
for document in hubCollection.find():
    print (document)
for document in hubStates.find():
    print (document)
for document in hubUsers.find():
    print (document)

client.close()
