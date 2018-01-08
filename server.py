#!/usr/bin/python

from __future__ import division
import os.path
import os
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import serverMethods
import serverDB
import switchboard
from switchboard import *
from bson import json_util
from tornado import gen
import json
from sockjs.tornado import SockJSRouter, SockJSConnection
from time import time
from hashlib import md5
from random import random


class AppSocketConnection(SockJSConnection):
    def on_open(self, request):
        i = md5()
        i.update('%s%s' % (random(), time()))
        self.appSocketID = i.hexdigest()
        self.authenticated = False
        print("New App Socket connection. ID: %s" % self.appSocketID)
        self.send(json.dumps({'type': 'init', 'appSocketID': self.appSocketID}))

    def on_message(self, message):
        print("New MESSAGE from App")
        msg = json.loads(message)
        if msg['appSocketID'] != self.appSocketID:
            return False
        if not self.authenticated and msg['type'] != 'auth':
            self.send(json.dumps({'type': 'error'}))
            return False
        elif msg['type'] == 'auth':
            self.user = msg['user']
            passcode = msg['passcode']
            error = serverDB.loginUser(self.user, passcode)
            if not error:
                self.authenticated = True
                print("App Client Authenticated")
            else:
                self.send(json.dumps({'type': 'error', 'reason': 'auth_fail'}))
                return False
            if self.user not in serverDB.appSocketList:
                serverDB.appSocketList[self.user] = []
            serverDB.appSocketList[self.user].append(self)

            device = serverDB.findUserHub(self.user)
            nodeList = {}
            if device:
                nodeList = serverDB.findHub(device)
            nodeList['type'] = 'stateChange'
            if '_id' in nodeList:
                del nodeList['_id']
            if serverDB.checkHubActive(device) is False:
                # Make hub offline
                print(nodeList)
            msg = json.dumps(nodeList, default=json_util.default)
            self.send(msg)
        elif msg['type'] == 'singleSwitchUpdate':
            hubAddr = msg['hubAddr']
            nodeid  = msg['nodeid']
            print("Got singleSwitchUpdate from App")
            print(hubAddr)
            print(nodeid)
            found = 0

            if int(hubAddr) in serverDB.connectionList:
                conn = serverDB.connectionList[int(hubAddr)]
                nodeList = serverDB.findHub(int(hubAddr))
                boardStr = "board" + nodeid

                if boardStr in nodeList:
                    node = nodeList[boardStr]
                    Msg = serverMethods.sentStateChangeReqForApp(node['devIndex'], node['type'], msg)
                    serverMethods.messageNum += 1  #
                    serverMethods.messageList[serverMethods.messageNum] = 0

                    print("sent state change")
                    Msg.update({'mid': serverMethods.messageNum})
                    print(Msg)
                    conn.write_message(Msg)
                    found = 1
                else:
                    found = 0

            if (found == 0):
                self.send(json.dumps({'type': 'error', 'reason': 'Device not found'}))
            else:
                # Async Wait for info response.
                # Fetch and send result.
                i = 0
                while (i < 20 and serverMethods.messageList[serverMethods.messageNum] == 0):
                #    yield gen.sleep(0.2)
                    i += 1
                print("yield sleep sec(s),active list is")
                print(serverMethods.messageList)
                print(i / 5)
                del serverMethods.messageList[serverMethods.messageNum]

                nodeList = serverDB.findHub(int(hubAddr))

                # Update All clients...
                nodeList['type'] = 'stateChange'
                nodeList['socketId'] = 0
                nodeList['appSocketID'] = self.appSocketID
                if '_id' in nodeList:
                    del nodeList['_id']
                msg = json.dumps(nodeList, default=json_util.default)
                if self.user in serverDB.socketList:
                    print("sending to users:%d" % len(serverDB.socketList[self.user]))
                    SocketConnection.broadcast(serverDB.socketList[self.user][0],
                                               serverDB.socketList[self.user], msg)
                if self.user in serverDB.appSocketList:
                    print("sending to apps:%d" % len(serverDB.appSocketList[self.user]))
                    AppSocketConnection.broadcast(serverDB.appSocketList[self.user][0],
                                                  serverDB.appSocketList[self.user], msg)

    def on_close(self):
        print("App socket CLOSED")
        if self.user in serverDB.appSocketList:
            if self in serverDB.appSocketList[self.user]:
                serverDB.appSocketList[self.user].remove(self)

class SocketConnection(SockJSConnection):
    def on_open(self, request):
        i = md5()
        i.update('%s%s' % (random(), time()))
        self.socketID = i.hexdigest()
        self.authenticated = False
        print("New socket connection. id:%s" % self.socketID)
        self.send(json.dumps({'type': 'init', 'socketId': self.socketID}))

    def on_message(self, msg):
        print("message came from browser socket: %s" % msg)
        msg = json.loads(msg)
        if msg['socketId'] != self.socketID:
            return False

        if not self.authenticated and msg['type'] != 'auth':
            self.send(json.dumps({'type': 'error'}))
            return False
        elif msg['type'] == 'auth':
            # session ID Authentication.
            self.sessionId = msg['sessionId']
            self.user = msg['user']
            if self.sessionId not in serverDB.sessionList[self.user]:
                # Force a page refresh at the client side to start a new session,
                # As the requested session is not found.
                self.send(json.dumps({'type': 'error'}))
                return False
            else:
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

        if self.user in serverDB.sessionList:
            if self.sessionId in serverDB.sessionList[self.user]:
                serverDB.sessionList[self.user].remove(self.sessionId)
        print("session closed")
        print("session list")
        print(serverDB.sessionList)



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

        i = md5()
        i.update('%s%s' % (random(), time()))
        sessionId = i.hexdigest()
        if self.current_user not in serverDB.sessionList:
            serverDB.sessionList[self.current_user] = []
        serverDB.sessionList[self.current_user].append(sessionId)

        if serverDB.checkHubActive(device) is False:
            device = 0

        self.render("index.html", nodes=nodeList, hubid=device, sessionId=sessionId)


class Devhandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New device connection\n")

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

    def on_ping(self, data):
        print("received ping")

    def on_pong(self, data):
        print("received ping reply")


class Userhandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def post(self, hubAddr, nodeid):
        print("Message from user %s, hubAddr:%s nodeid:%s" % (self.current_user, hubAddr, nodeid))
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
            nodeList['appSocketID'] = '0'
            if '_id' in nodeList:
                del nodeList['_id']
            msg = json.dumps(nodeList, default=json_util.default)
            if self.current_user in serverDB.socketList:
                print("sending to browsers:%d" % len(serverDB.socketList[self.current_user]))
                if len(serverDB.socketList[self.current_user]) != 0:
                    SocketConnection.broadcast(serverDB.socketList[self.current_user][0], serverDB.socketList[self.current_user], msg)
            if self.current_user in serverDB.appSocketList:
                print("sending to apps:%d" % len(serverDB.appSocketList[self.current_user]))
                if len(serverDB.appSocketList[self.current_user]) != 0:
                    AppSocketConnection.broadcast(serverDB.appSocketList[self.current_user][0], serverDB.appSocketList[self.current_user], msg)


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

        error = serverDB.checkHubValid(hubid)
        if not error:
            error = serverDB.addUser(username, password)
            if not error:
                error = serverDB.registerHub(username, hubid)
                if not error:
                    self.redirect("/login")
                else:
                    self.render("login.html", logintype = "signup", errorString = error)
            else:
                self.render("login.html", logintype = "signup", errorString = error)
        else:
               self.render("login.html", logintype = "signup", errorString = error)


def main():
    SocketRouter = SockJSRouter(SocketConnection, '/socket')
    AppRouter = SockJSRouter(AppSocketConnection, '/app')
    app = tornado.web.Application(
        SocketRouter.urls +
        AppRouter.urls +
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
        websocket_ping_interval = 40,
        websocket_ping_timeout = 120,
    )
    serverDB.initDatabase()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(os.environ.get('PORT'))
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
