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
from time import sleep

remote_server = None


class Mainhandler(tornado.web.RequestHandler):
    def get(self): 
        if serverDB.devClientConnection is None:
            device = 0
        else:
            device = 1
        nodeList = {}
        nodeList = serverDB.getHubState()

        i = md5()
        i.update('%s%s' % (random(), time()))
        sessionId = i.hexdigest()

        self.render("index.html", nodes=nodeList, hubid=device, sessionId=sessionId)


class Devhandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("dev_client connection\n")

    def on_message(self, message):
        global remote_server
        serverMethods.processMsgFromClient(self, remote_server, message)

    def on_close(self):
        serverDB.devClientConnection = None
        print("Closed dev_client connection\n")

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

        conn = serverDB.devClientConnection
        if conn is not None:
            nodeList = serverDB.getHubState()
            boardStr = "board" + nodeid

            if boardStr in nodeList:
                node = nodeList[boardStr]
                Msg = serverMethods.prepareStateChangeReq(node['devIndex'], node['type'], self)
                conn.write_message(Msg)
                found = 1
            else:
                found = 0
        else:
            print("Dev_client connection not found\n")
        '''
        TODO : Sent this message properly to global server as well
        TODO : DO the async update all user connection thing
        '''
        if (found == 0):
            self.write("Device not found\n")
        else:
            self.redirect(self.get_argument("next"))

@gen.coroutine
def connect_server():
    '''
    TODO : Do the read message from global server and self identification, auth, ip etc
    '''
    global remote_server
    while remote_server is None:
        try:
            remote_server= yield tornado.websocket.websocket_connect("ws://dotslash.co/dev")
        except:
            print("Connection Refused try again in 5")
            sleep(5)
        else:
            print("Connected to global server")

@gen.coroutine
def global_server_read():
    global remote_server
    yield connect_server()

    while 1:
        msg = yield remote_server.read_message()
        if msg:
            if  serverDB.devClientConnection is not None:
                serverDB.devClientConnection.write_message(msg)
                print("Message from global server")
                print(msg)
        else:
            yield connect_server()

    remote_server.close()

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
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().run_sync(global_server_read)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
