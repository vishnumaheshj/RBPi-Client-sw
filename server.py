#!/usr/bin/python

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serverMethods
import serverDB
from bson import json_util
from tornado import gen
import json


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class Mainhandler(BaseHandler):
    @tornado.web.authenticated
    def get(self): 
        device = serverDB.findUserHub(self.current_user)
        print("Device of user %s:%d" %(self.current_user, device))
        nodeList = {}
        if device:
            nodeList = serverDB.findHub(device)

        if serverDB.checkHubActive(device) is False:
            device = 0
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
                serverDB.makeHubOffline(serverDB.connectionList.inv[self])
                del serverDB.connectionList.inv[self]
                print("closed connection \n")
                print("connection list")
                print(serverDB.connectionList)
            else:
               print("\nunknown connection closed")


class Userhandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def post(self, hubAddr, nodeid):
        print("Message from user %s, hubAddr:%s nodeid:%s" %(self.current_user, hubAddr, nodeid))
        found = 0

        # ADD CHECK FOR HUB IN USER DATABASE.
        #device = serverDB.findUserHub(self.current_user)
        #print("device of user %s:%d" % (self.current_user, device))
        #if device:
        #    nodeList = serverDB.findHub(device)

        if int(hubAddr) in serverDB.connectionList: 
                conn = serverDB.connectionList[int(hubAddr)]
                nodeList = serverDB.findHub(int(hubAddr))
                boardStr = "board" + nodeid

                if boardStr in nodeList:
                    node = nodeList[boardStr]
                    Msg = serverMethods.sentStateChangeReq(node['devIndex'], node['type'], self)
                    #  serverMethods.activeNum = serverMethods.activeNum + 1    # Later
                    serverMethods.activeList[serverMethods.activeNum] = 0
                    
                    print("sent state change")
                    Msg.update({'mid': serverMethods.activeNum})
                    print(Msg)
                    conn.write_message(Msg)
                    found = 1
                else:
                    found = 0
        if (found == 0):
            self.write("Device not found\n")
        else:
            # Async Wait for info response.
            # Fetch and send result.
            i = 0
            while(i < 4 and serverMethods.activeList[serverMethods.activeNum] == 0):
                yield gen.sleep(1)
                i = 1 + 1
            print("i:%d,active list" % i)
            print(serverMethods.activeList)
            
            nodeList = serverDB.findHub(int(hubAddr))
            self.write(json.dumps(nodeList, default=json_util.default))

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = tornado.escape.xhtml_escape(self.get_argument("password"))
        print("username:%s" % username)
        print("password %s" % password)

        error = serverDB.loginUser(username, password)
        if not error:
            self.set_secure_cookie("username", username)
            self.redirect(self.get_argument("next", "/"))
        else:
            self.render("login.html", errorString = error)


class LogoutHandler(BaseHandler):
    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))

        serverDB.logoutUser(username)
        self.clear_cookie("username")
        self.redirect("/")

class SignupHandler(BaseHandler):
    def get(self):
        self.render("login.html", logintype="signup")

    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = tornado.escape.xhtml_escape(self.get_argument("password"))
        hubid = int(tornado.escape.xhtml_escape(self.get_argument("hubid")))
        print("username:%s" % username)
        print("password %s" % password)
        print("HudId %d" % hubid)

        error = serverDB.addUser(username, password)
        if not error:
            error = serverDB.registerHub(username, hubid)
            if not error:
                self.redirect("/login")
            else:
                self.render("login.html", logintype = "signup", errorString = error)
        else:
            self.render("login.html", logintype = "signup", errorString = error)

def main():
    app = tornado.web.Application(
        [
            (r"/", Mainhandler),
            (r"/dev", Devhandler),
            (r"/user/([0-9]+)/([0-9]+)", Userhandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/signup", SignupHandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret = "98RaTgemQjS/zVMMFr8oZ35z9S1UsEaGgl/E3cpxm/E=",
        login_url = "/login",
        xsrf_cookies = "True",
        degug = "True",
    )
    serverDB.initDatabase()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
