#!/usr/bin/python

from __future__ import division
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
from sockjs.tornado import SockJSRouter, SockJSConnection
from sets import Set
from time import time
from hashlib import md5
from random import random


class SocketConnection(SockJSConnection):
    def on_open(self, request):
        i = md5()
        i.update('%s%s' % (random(), time()))
        socketId = i.hexdigest()
        self.socketID = socketId
        self.authenticated = False
        print("New socket connection. id:%s" % self.socketID)
        self.send(json.dumps({'type':'init', 'socketId': socketId}))

    def on_message(self, msg):
        print("message came from browser socket: %s" % msg)
        msg = json.loads(msg)
        if msg['socketId'] != self.socketID:
            return False

        if not self.authenticated and msg['type'] != 'auth':
            return False
        elif msg['type'] == 'auth':
            # Authentication to be added
            self.user = msg['user']
            self.authenticated = True
            if self.user not in serverDB.socketList:
                serverDB.socketList[self.user] = []
            serverDB.socketList[self.user].append(self)

        print("socket list")
        print(serverDB.socketList)

    def on_close(self):
        print("socket connection closed")
        if self.user in serverDB.socketList:
            if self in serverDB.socketList[self.user]:
                serverDB.socketList[self.user].remove(self)
        print("socket list")
        print(serverDB.socketList)


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
        print(self.request.arguments)
        sid = self.get_argument('socketId', default=None)
        if sid is not None:
            print("socket id of ajax request:%s" % sid)

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
                    serverMethods.messageNum += 1       #
                    serverMethods.messageList[serverMethods.messageNum] = 0
                    
                    print("sent state change")
                    Msg.update({'mid': serverMethods.messageNum})
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
            while (i < 20 and serverMethods.messageList[serverMethods.messageNum] == 0):
                yield gen.sleep(0.2)
                i += 1
            print("yield sleep sec(s),active list is")
            print(serverMethods.messageList)
            print(i/5)
            del serverMethods.messageList[serverMethods.messageNum]
            
            nodeList = serverDB.findHub(int(hubAddr))
            msg = json.dumps(nodeList, default=json_util.default)
            self.write(msg)
            # Update other clients...
            nodeList['serverPush'] = 'stateChange'
            nodeList['socketId'] = sid
            msg = json.dumps(nodeList, default=json_util.default)
            print("sending to users:%d" % len(serverDB.socketList[self.current_user]))
            SocketConnection.broadcast(serverDB.socketList[self.current_user][0], serverDB.socketList[self.current_user], msg)



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
    SocketRouter = SockJSRouter(SocketConnection, '/socket')
    app = tornado.web.Application(
        SocketRouter.urls +
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
