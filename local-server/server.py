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
from time import time
from hashlib import md5
from random import random



class Mainhandler(tornado.web.RequestHandler):
    def get(self): 
        device = 1
        nodeList = {}
        nodeList = serverDB.findHub()

        i = md5()
        i.update('%s%s' % (random(), time()))
        sessionId = i.hexdigest()
        if self.current_user not in serverDB.sessionList:
            serverDB.sessionList[self.current_user] = []
        serverDB.sessionList[self.current_user].append(sessionId)

        if serverDB.checkHubActive() is False:
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


class Userhandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self, hubAddr, nodeid):
        print("Message from user %s, hubAddr:%s nodeid:%s" % (self.current_user, hubAddr, nodeid))
        found = 0
        print(self.request.arguments)
        sid = self.get_argument('socketId', default=None)
        if sid is not None:
            print("socket id of ajax request:%s" % sid)

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


def main():
    app = tornado.web.Application(
        [
            (r"/", Mainhandler),
            (r"/dev", Devhandler),
            (r"/user/([0-9]+)/([0-9]+)", Userhandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies = "True",
        degug = "True",
    )
    serverDB.initDatabase()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
