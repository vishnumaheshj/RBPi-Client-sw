import tornado.websocket
from tornado import gen
import ctypes
from ctypes import cdll
import clientMethods
import json

@gen.coroutine
def dev_connect():
    lib = cdll.LoadLibrary("./libshm.so")
    readId = lib.init_read_shm()
    writeId = lib.init_write_shm()
    inMsg = clientMethods.sbMessage_t()

    #client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
    client = yield tornado.websocket.websocket_connect("ws://localhost:8880/dev")
    msg = yield client.read_message()
    print("%s\n" % msg)
    client.write_message("001")
    while 1:
        msg = yield client.read_message()
        print("Message is %s" % msg)
        Msg = json.loads(msg)

        Req = clientMethods.createMessageForHub(Msg)

        lib.write_shm(clientMethods.byref(Req), writeId)

        lib.read_shm(clientMethods.byref(inMsg), readId)

        serReq = clientMethods.createMessageForServer(inMsg)

        client.write_message(json.dumps(serReq))

        continue
    client.close()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
