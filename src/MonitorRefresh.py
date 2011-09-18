__author__ = "Pascal Richier <dieu9000@hotmail.com>"
__version__ = "0.0"
__date__ = "16 September 2002"

import socket
import Protocol
import threading
import Monitor
import time
import sys
import string
import select

class MonitorRefresh(threading.Thread):
    """This class is an abstraction of the MonitorRefresh.
    It is instanciated each time that refresh frequeone change
    or that that refresh button is activated."""
    
    __refresh_ability = 1
    

    def __init__(self,
                 monitor,
                 config):
        threading.Thread.__init__(self)

        self.loop = 1
        self.monitor = monitor
        self.server = config["scheduler_address"]
        self.__socket_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.__socket_send.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
        self.socket_taget = (config["scheduler_address"],
                             Protocol.SCHEDULER_DAEMON_PORT_INFO)
        self.__socket_send.setblocking(0)
        
        self.__listen_socket = socket.socket(socket.AF_INET,\
                                             socket.SOCK_DGRAM)
        
    def run(self):
        while self.loop:
            if self.monitor.gLock == 0:
                self.monitor.gInCom = 1
                try:
                    self.__socket_send.sendto(Protocol.REQUEST_INFO, self.socket_taget)
                    data = self.__socket_send.recv(65535)
                except socket.error, SendUDPFailure:
                    self.monitor.gInCom = 1
                else:
                    self.monitor.gLock = 1
                    self.monitor.gInCom = 0
                    if self.monitor.gData != data:
                        self.monitor.gData = data
                        self.monitor.gMaj = 1
            time.sleep(0.2)

    def send_info_query(self):
        try:
            self.__socket_send.sendto(Protocol.REQUEST_INFO,self.socket_taget)
        except socket.error:
            self.monitor.gInCom = 1          

    def stop_loop(self):
        self.loop = 0
