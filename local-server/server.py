#!/usr/bin/python

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen
import subprocess

class Mainhandler(tornado.web.RequestHandler):
    def get(self): 
        self.redirect("/signup")

class WifiHandler(tornado.web.RequestHandler):
    def get(self):
        out = subprocess.check_output("sudo iw dev 'wlan0' scan ap-force | egrep 'SSID:' | cut -d ':' -f2", shell = True)
        wifi_list = list(filter(None, out.split('\n')))
        self.render("wifi.html", ssids=wifi_list)

class SignupHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html", logintype="signup")

    def post(self):
        hubid = tornado.escape.xhtml_escape(self.get_argument("hubid"))

        execute = "mkpasswd " + hubid + " -m sha-512 -S asdfghjkl"
        hash_cur = subprocess.check_output(execute, shell = True)
        hash_cur = hash_cur[:-1]
        dot_file = open("/etc/dotshadow", "r")
        hash_ori = dot_file.read()
        dot_file.close()

        if hash_cur == hash_ori:
            self.redirect("/wifi")
        else:
            self.render("login.html", logintype="signup", errorString = "Invalid Hub Address")

def main():
    app = tornado.web.Application(
        [
            (r"/", Mainhandler),
            (r"/signup", SignupHandler),
            (r"/wifi", WifiHandler),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "static"),
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
