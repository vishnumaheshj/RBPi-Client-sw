import tornado.websocket
from tornado import gen
import ctypes
from ctypes import cdll

@gen.coroutine
def dev_connect():
	lib = cdll.LoadLibrary("/home/dotslash/dotslash/tornado_backend/shared/libshm.so")
	id = lib.init_shm()
	#client = yield tornado.websocket.websocket_connect("ws://192.168.0.106:8888/dev")
	client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
	msg = yield client.read_message()
	print("Message is %s\n" % msg)
	client.write_message("001")
	while 1:
		msg = yield client.read_message()
		print("Message is %s\n" % msg)
		lib.update_shm(ctypes.create_string_buffer(msg), id)
		continue
	client.close()

if __name__ == "__main__":
	tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
