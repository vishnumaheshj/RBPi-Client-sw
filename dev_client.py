import tornado.websocket
from tornado import gen
import ctypes
import subprocess
from threading import Thread

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

@gen.coroutine
def dev_connect():
	#shm related initializations
	lib = ctypes.cdll.LoadLibrary("/home/dotslash/dotslash/tornado_backend/shared/libshm.so")
	shm_id = lib.init_shm()

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

	#Connect to server
	#client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
	client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
	msg = yield client.read_message()
	print("%s\n" % msg)
	client.write_message("001")
	while 1:
		msg = yield client.read_message()
		print("Server Message is %s\n" % msg)
		lib.update_shm(ctypes.create_string_buffer(msg), shm_id)
		continue
	client.close()

if __name__ == "__main__":
	tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
