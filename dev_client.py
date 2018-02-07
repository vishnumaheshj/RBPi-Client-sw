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
import logging

#globals
client = None
#Global variable to ensure that client connects to server only after successfully initializing ZNP 
binary_init_status = 0
dev_ready_ntf = {}

def init_log(log_level):
    logging.basicConfig(filename = '/home/pi/dotslash/client/client.log', format = "%(asctime)s:%(levelname)s: %(message)s", level = log_level)

#Method to run ZNP init binary
def execute_binary():
    global binary_init_status
    binary = subprocess.Popen("/home/pi/dotslash/client/dataSendRcv.bin", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while binary.poll() is None:
        line =  binary.stdout.readline()
        logging.info("dataSendRcv.bin : %s" %line)
        if line != '':
            if b'Error' in line:
                logging.error(line)
                binary_init_status = -1
                binary.terminate()
                break
            if b'Done' in line:
                binary_init_status = 1


def listen_hub():
    logging.info("@@..listening hub..@@")
    global dev_ready_ntf
    global client
    inMsg = clientMethods.sbMessage_t()
    dev_ready_ntf = clientMethods.initializeHub()
    while True:
        clientMethods.readShm(inMsg)
        logging.info("listenHub:new message")
        serReq = clientMethods.createMessageForServer(inMsg)
        while client is None:
            sleep(1)
            continue
        client.write_message(json.dumps(serReq))
        logging.info("listenHub:send message")
        continue 


@gen.coroutine
def connect_server():
    global client
    client = None
    while client is None:
        try:
            client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
            #client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
            #client = yield tornado.websocket.websocket_connect("ws://dotslash.co/dev")
        except:
            logging.error("Connection Refused try again in 5")
            sleep(5)
        else:
                global dev_ready_ntf
                client.write_message(json.dumps(dev_ready_ntf))
                logging.info("Connection established")


@gen.coroutine
def dev_connect():

    #Execute dataSendRcv binary on separate thread
    thread = Thread(target = execute_binary)
    thread.daemon = True
    thread.start()
    logging.info("Initializing ZNP")
    global binary_init_status
    while binary_init_status== 0:
        continue
    if binary_init_status== -1:
        logging.error("Could not initialize ZNP device")
        return
    else:
        logging.info("ZNP init success, connecting to server")

    thread = Thread(target = listen_hub)
    thread.daemon = True
    thread.start()
    
    global dev_ready_ntf 
    global client
    while not dev_ready_ntf:
            sleep(1)
            continue
    yield connect_server()
    logging.info("$$....dev connect....$$")
    while 1:
        msg = yield client.read_message()
        logging.info("From dev connect:%s" % msg)
        if msg:
            Msg = json.loads(msg)
            Req = clientMethods.createMessageForHub(Msg)
            clientMethods.writeShm(Req)
            logging.info("From dev connect: send to hub")
        else:
            yield connect_server()
    client.close()

if __name__ == "__main__":
    init_log(logging.DEBUG)
    tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
