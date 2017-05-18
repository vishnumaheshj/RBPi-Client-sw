import tornado.websocket
from tornado import gen
import clientMethods
import json
#import concurrent.futures
import ctypes
import subprocess
from threading import Thread

client = None

#Global variable to ensure that client connects to server only after successfully initializing ZNP 
binary_init_status = 0

#Method to run ZNP init binary
def execute_binary():
    global binary_init_status
    binary = subprocess.Popen("./dataSendRcv.bin", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while binary.poll() is None:
        line =  binary.stdout.readline()
        if line != '':
            if "Error" in line:
                print(line)
                binary_init_status = -1
                binary.terminate()
                break
            if "Enter message" in line:
                binary_init_status = 1

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

#executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
#a = executor.submit(listen_hub)


@gen.coroutine
def dev_connect():
    #Execute dataSendRcv binary on separate thread
    thread = Thread(target = execute_binary)
    thread.daemon = True
    thread.start()
    print("Initializing ZNP")
    while binary_init_status== 0:
        continue
    if binary_init_status== -1:
        print("Could not initialize ZNP device")
        return
    else:
        print("ZNP init success, connecting to server")

    thread = Thread(target = listen_hub)
    thread.daemon = True
    thread.start()
    
    print("$$....dev connect....$$")
    clientMethods.checkInit()
    global client
    #Connect to server
    #client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
    client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
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
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
