import tornado.websocket
from tornado import gen
import clientMethods
import json
#import concurrent.futures
import ctypes
import subprocess
from threading import Thread
from time import sleep
import switchboard
from switchboard import *

#globals
client = None
#Global variable to ensure that client connects to server only after successfully initializing ZNP 
binary_init_status = 0
dev_ready_ntf = {}

#Method to run ZNP init binary
def execute_binary():
    global binary_init_status
    binary = subprocess.Popen("./dataSendRcv.bin", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while binary.poll() is None:
        line =  binary.stdout.readline()
        print("dataSendRcv.bin : %s" %line)
        if line != '':
            if b'Error' in line:
                print(line)
                binary_init_status = -1
                binary.terminate()
                break
            if b'Done' in line:
                binary_init_status = 1

def listen_hub():
    print("@@..listening hub..@@")
    global dev_ready_ntf
    global client
    inMsg = clientMethods.sbMessage_t()
    dev_ready_ntf = clientMethods.initializeHub()
    while True:
        clientMethods.readShm(inMsg)
        print("listenHub:new message")
        serReq = clientMethods.createMessageForServer(inMsg)
        while client is None:
            sleep(1)
            continue
        client.write_message(json.dumps(serReq))
        print("listenHub:send message")
        continue 

@gen.coroutine
def connect_server():
    global client
    client = None
    while client is None:
        try:
            #client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
            #client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
            client = yield tornado.websocket.websocket_connect("ws://dotslash.co/dev")
        except:
            print("Connection Refused try again in 5")
            sleep(5)
        else:
                global dev_ready_ntf
                client.write_message(json.dumps(dev_ready_ntf))
                print("Connection established")

@gen.coroutine
def dev_connect():

    #Execute dataSendRcv binary on separate thread
    thread = Thread(target = execute_binary)
    thread.daemon = True
    thread.start()
    print("Initializing ZNP")
    global binary_init_status
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
    
    global dev_ready_ntf 
    global client
    while not dev_ready_ntf:
            sleep(1)
            continue
    yield connect_server()
    print("$$....dev connect....$$")
    while 1:
        msg = yield client.read_message()
        print("From dev connect:%s" % msg)
        if msg:
            Msg = json.loads(msg)
            if Msg['message_type'] == SB_KEEP_ALIVE:
                client.write_message(msg)
                print("From dev connect: send keep alive resp")
                
            else:
                Req = clientMethods.createMessageForHub(Msg)
                clientMethods.writeShm(Req)
                print("From dev connect: send to hub")
        else:
            yield connect_server()
    client.close()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
