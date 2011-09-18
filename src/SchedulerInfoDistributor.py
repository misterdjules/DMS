__author__ = "Pascal Richier <dieu9000@hotmail.com>"
__version__ = "0.0"
__date__ = "16 September 2002"

import socket
import Protocol
import ProtocolUtils
import threading
import string
import CompilerStore
import CompilerDistributor
import syslog
import sys

class SchedulerInfoDistributor(threading.Thread):
    """This class is an abstraction of the inforation
    distributor.
    It is instanciated one time by the scheduler daemon
    it receives a request from a monitor and send it all
    informations avaibles."""

    def __init__(self):
        
        threading.Thread.__init__(self)
        
        self.__listen_socket = socket.socket(socket.AF_INET,\
                                             socket.SOCK_DGRAM)
        self.__listen_socket.bind(("", Protocol.SCHEDULER_DAEMON_PORT_INFO))

    def run(self):
        while 1:
            try:           
                data, sender = self.__listen_socket.recvfrom(65535)
                self.__listen_socket.sendto(CompilerDistributor.CompilerDistributor.store.get_info(),
                                             sender)
            except socket.error:
                syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON,\
                              "tring to receiv but break")
                sys.exit(1)

            

    
