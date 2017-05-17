import tornado.websocket
from tornado import gen
import clientMethods
import json

@gen.coroutine
def dev_connect():
    inMsg = clientMethods.sbMessage_t()

    serReq = clientMethods.initializeHub()
    #client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
    client = yield tornado.websocket.websocket_connect("ws://localhost:8880/dev")
    msg = yield client.read_message()
    print("%s\n" % msg)
    client.write_message(json.dumps(serReq))
    while 1:
        msg = yield client.read_message()
        print("Message is %s" % msg)
        Msg = json.loads(msg)

        Req = clientMethods.createMessageForHub(Msg)

        clientMethods.writeShm(Req)
        clientMethods.readShm(inMsg)

        serReq = clientMethods.createMessageForServer(inMsg)

        client.write_message(json.dumps(serReq))

        continue
    client.close()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
