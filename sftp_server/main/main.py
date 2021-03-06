#!/usr/bin/env python
# encoding:utf-8

__author__ = 'xiaopeng'

import socketserver
import time
import sys
import os
import threading
import json
Base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_dir)
from conf.json_handle import Json_handle


class MyTCPHandler(socketserver.BaseRequestHandler):
    def Get(self,*args):
        print("aaaaa")
        self.request.send(b'success')

    def Create(self,*args):
        print("bbbbb")
        data = json.loads(self.data.decode())
        print(data["action"], data["user_name"], data["password"])
        Json_handle(data["user_name"],data).Write()
        os.popen('mkdir /home/%s' %(data["user_name"])).read()
        os.popen('useradd -s /sbin/nologin %s' %(data["user_name"])).read()
        os.popen('chown -R %s.%s /home/%s' %(data["user_name"],data["user_name"],data["user_name"])).read()
        command_reslut = os.popen('ls -d /home/%s' %(data["user_name"])).read()
        print(command_reslut)
        self.request.send(command_reslut.encode("utf-8"))
        print("ccccc")

    def Login(self,*args):
        data = json.loads(self.data.decode())
        print(data)
        Json_result = Json_handle(data["user_name"],data).ReadJson()
        print(Json_result)
        self.request.send("用户登录成功".encode("utf-8"))

    def Home(self,*args):
        data = json.loads(self.data.decode())
        print(data)
        Json_result = data["command"].strip()
        if Json_result.split()[0] == "mkdir":
            command_result = os.popen('%s /home/%s/%s' %(Json_result.split()[0], data["home"],Json_result.split()[1])).read()
            os.popen('chmod %s.%s /home/%s/%s' %(data["user_name"],data["user_name"],data["home"],Json_result.split()[1]))
        else:
            command_result = os.popen('%s /home/%s' %(Json_result, data["home"])).read()
        print(command_result)
        self.request.send(command_result.encode("utf-8"))

    def handle(self):
        while True:
            print(self.client_address[0])
            self.data = self.request.recv(1024).strip()
            print(self.data)
            cms_result = json.loads(self.data.decode())
            action = cms_result["action"]
            if hasattr(self, action):
                func = getattr(self,action)
                func(cms_result)
            else:
                print("the methond is not.")
                self.request.send(b'404')


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
