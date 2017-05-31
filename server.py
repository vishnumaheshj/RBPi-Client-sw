#!/usr/bin/python

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serverMethods
import serverDB

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
	    return self.get_secure_cookie("username")


class Mainhandler(BaseHandler):
    @tornado.web.authenticated
    def get(self): 
        device = 0
        nodeList = {}
        devices = serverDB.connectionList.keys()
#Hardcoding hub as device[0]
        if devices:
            device = list(devices)[0]
        nodeList = serverDB.findHub(device)
        if nodeList:
                del nodeList["_id"]
                del nodeList["hubAddr"]
                del nodeList["totalNodes"]
        self.render("index.html", nodes = nodeList, hubid = device)

class Devhandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New device connection\n")
        self.write_message("Server accepted connection\n")

    def on_message(self, message):
        serverMethods.processMsgFromClient(self, message)

    def on_close(self):
            if self in serverDB.connectionList.inv:
                print("\nclosing connection for %d" % serverDB.connectionList.inv[self])
                makeHubOffline(serverDB.connectionList.inv[self])
                del serverDB.connectionList.inv[self]
                print("closed connection \n")
                print("connection list")
                print(serverDB.connectionList)
            else:
               print("\nunknown connection closed")

class Userhandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, hubAddr, nodeid):
        print("Message from user")
        found = 0
        if int(hubAddr) in serverDB.connectionList: 
                conn = serverDB.connectionList[int(hubAddr)]
                node = serverDB.findNode(int(hubAddr), int(nodeid))
                if node is not None:
                    Msg = serverMethods.sentStateChangeReq(node['devIndex'], node['type'], self)
                    conn.write_message(Msg)
                    found = 1
                else:
                    found = 0
        if (found == 0):
            self.write("Device not found\n")
        else:
            #self.write("Message sent successfully\n")
            self.redirect(self.get_argument("next"))

class LoginHandler(BaseHandler):
    def get(self):
	    self.render("login.html")
	
    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))
        self.redirect("/")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.redirect("/")


def main():
    app = tornado.web.Application(
        [
            (r"/", Mainhandler),
            (r"/dev", Devhandler),
            (r"/user/([0-9]+)/([0-9]+)", Userhandler),
			(r"/login", LoginHandler),
			(r"/logout", LogoutHandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
		cookie_secret = "98RaTgemQjS/zVMMFr8oZ35z9S1UsEaGgl/E3cpxm/E=",
		login_url = "/login"
    )
    serverDB.initDatabase()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
