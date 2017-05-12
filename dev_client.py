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

        inMsg = clientMethods.sbMessage_t()

        lib.read_shm(clientMethods.byref(inMsg), readId)

        client.write_message(inMsg)

        continue
    client.close()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
