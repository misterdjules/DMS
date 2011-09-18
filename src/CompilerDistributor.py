__author__ = "Pascal Richier <dieu9000@hotmail.com>"
__version__ = "0.0"
__date__ = "16 August 2002"

import socket
import Protocol
import ProtocolUtils
import threading
import string
import signal
import os
import sys
import syslog
import CompilerInformation
import CompilerStore

class CompilerDistributor(threading.Thread):
    """This class is an abstraction of a remote host.
    It is instanciated by the scheduler daemon each time
    it receives a request from a compiler client."""

    store = CompilerStore.CompilerStore()
    __lock = threading.Lock()

    def __init__(self, socket, address):
        """The socket argument is the one used to communicate
        with the client that has requested the host"""
        threading.Thread.__init__(self)
        self.__client_socket = socket
        self.__client_address, self.__client_port = address

    def run(self):
        request_type = ProtocolUtils.recv_data(self.__client_socket)
        if (request_type == Protocol.REQUEST_HOST):
            self.request_host()
        elif (request_type == Protocol.RECORD_ME):
            self.record_host()
        elif (request_type == Protocol.UNSUBSCRIBE_ME):
            self.unsubscribe()
        elif (request_type == Protocol.JOB_DONE):
            self.job_done()
        else:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler receve Unknown Message from "\
                          + self.__client_address\
                          + ":%s"%(self.__client_port))
            print "Unknown Message" + request_type
        self.__client_socket.close()

    def request_host(self):
        host = self.store.give_host()
        ProtocolUtils.send_data(self.__client_socket, host)
        syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                      "dms Scheduler give host %s to client "%(host)\
                      + self.__client_address)

    def record_host(self):
        self.__lock.acquire()
        if self.__client_address in self.store.store.keys():
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler recev record request but host "\
                          + self.__client_address\
                          + " already registered")
        else:
            self.store.record_host(self.__client_address,\
                                   self.__client_port,\
                                   50)
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler record host "\
                          + self.__client_address)
        self.__lock.release()

    def unsubscribe(self):
        self.__lock.acquire()
        if self.__client_address in self.store.store.keys():
            self.store.remove_host(self.__client_address)
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler dms Scheduler unsubscibe host"\
                          + self.__client_address)
        else:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler try to unsubscibe host that is not in store"\
                          + self.__client_address)
        self.__lock.release()
        
            
    def job_done(self):
        nb_job = ProtocolUtils.recv_data(self.__client_socket)
        try:
            nb_job = string.atoi(nb_job)
        except:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler - receive bad information about"\
                          + " number of job in work by CompilerDaemon")
        else:
            self.store.set_nb_job_and_inc_count(self.__client_address, nb_job)
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "dms Scheduler receve DONE msg from host "\
                          + self.__client_address\
                          + ", actualy %s"%(nb_job) + " job in work")

    def get_store(self):
        return store
