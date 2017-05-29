#!/usr/bin/python

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serverMethods
from serverMethods import global_devlist

class Mainhandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", devices=global_devlist)

class Devhandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New device connection\n")
        self.write_message("Server accepted connection\n")

    def on_message(self, message):
        print("Message received %s\n" %message)
        serverMethods.processMsgFromClient(self, message)


    def on_close(self):
        for device in global_devlist:
            if(device.conn == self):
                global_devlist.remove(device)
                print("%s closed connection \n" % device.id)

class Userhandler(tornado.web.RequestHandler):
    def post(self, devid, nodeid):
        print("Message from user")
        found = 0
        for device in global_devlist:
            if(device.id == int(devid)):
                    for node in device.nodes:
                            if(node.id == int(nodeid)):
                                Msg = serverMethods.sentStateChangeReq(nodeid, node.type, self)
                                device.conn.write_message(Msg)
                                found =1
        if (found == 0):
            self.write("Device not found\n")
        else:
            self.write("Message sent successfully\n")



def main():
    app = tornado.web.Application(
        [
            (r"/", Mainhandler),
            (r"/dev", Devhandler),
            (r"/user/([0-9]+)/([0-9]+)", Userhandler)
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
