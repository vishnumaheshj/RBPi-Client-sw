import tornado.websocket
from tornado import gen
import clientMethods
import json
import concurrent.futures

client = None

def listen_hub():
    print("@@..listening hub..@@")
    inMsg = clientMethods.sbMessage_t()
    serReq = clientMethods.initializeHub()
    print("listenHub:%s", json.dumps(serReq))
    while (client == None):
            continue
    print("listenHub:clientHandle Ready")
    client.write_message(json.dumps(serReq))
    print("listenHub:Sent Device Ready..!!!!!@~~~~~~")
    while True:
        clientMethods.readShm(inMsg)
        print("listenHub:new message")
        serReq = clientMethods.createMessageForServer(inMsg)
        client.write_message(json.dumps(serReq))
        print("listenHub:send message")
        continue 

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
a = executor.submit(listen_hub)


@gen.coroutine
def dev_connect():
    print("$$....dev connect....$$")
    global client
    client = yield tornado.websocket.websocket_connect("ws://localhost:8880/dev")
    msg = yield client.read_message()
    print("From dev connect:%s" % msg)
    while 1:
        msg = yield client.read_message()
        print("From dev connect:%s" % msg)
        Msg = json.loads(msg)
        Req = clientMethods.createMessageForHub(Msg)
        clientMethods.writeShm(Req)
        print("From dev connect: send to hub")
        continue
    client.close()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(dev_connect)
