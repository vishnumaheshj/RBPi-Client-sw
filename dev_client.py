import tornado.websocket
from tornado import gen

@gen.coroutine
def dev_connect():
	client = yield tornado.websocket.websocket_connect("ws://localhost:8888/dev")
	msg = yield client.read_message()
	print("Message is %s\n" % msg)
	client.write_message("001")
	while 1:
		msg = yield client.read_message()
		print("Message is %s\n" % msg)
		continue
	client.close()

if __name__ == "__main__":
	tornado.ioloop.IOLoop.instance().run_sync(dev_connect)
