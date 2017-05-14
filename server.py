#!/usr/bin/python

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serverMethods
#from serverMethods import *

global_devlist = []

class dotslash_hub:
    def __init__(self,a,b):
        self.id = a
        self.conn = b

class Mainhandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", devices=global_devlist)

class Devhandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New device connection\n")
        self.write_message("Server accepted connection\n")

    def on_message(self, message):
        print("Message received %s\n" %message)
        device = dotslash_hub(message, self)
        global_devlist.append(device)
        print ("Devices %s" % global_devlist)
        serverMethods.processMsgFromClient(message)


    def on_close(self):
        for device in global_devlist:
            if(device.conn == self):
                global_devlist.remove(device)
                print("%s closed connection \n" % device.id)

class Userhandler(tornado.web.RequestHandler):
    def post(self):
        devid = self.get_argument('device', '')
        message = self.get_argument('message', '')
        print("Message from user %s" %message)
        print("Id %s\n" %devid)
        found = 0
        for device in global_devlist:
            if(device.id == devid):
                if (message[:4] == "cmd0"):
                    Msg = serverMethods.sentBoardInfoReq()
                    device.conn.write_message(Msg)
                elif (message[:4] == "cmd1"):
                    Msg = serverMethods.sentStateChangeReq()
                    device.conn.write_message(Msg)
                else:
                    device.conn.write_message(message)
                found = 1
        if (found == 0):
            self.write("Device not found\n")
        else:
            self.write("Message sent successfully\n")



def main():
    app = tornado.web.Application(
        [
            (r'/', Mainhandler),
            (r'/dev', Devhandler),
            (r'/user', Userhandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8880)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
