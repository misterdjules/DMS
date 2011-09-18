#!/usr/bin/env python

__author__ = "Julien Gilli <jgilli@nerim.fr>,\
Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "16 August 2002"

import socket
import Protocol
import ProtocolUtils
import pwd
import RemoteJob
import threading
import os
from Daemon import Daemon
import syslog
import commands
import sys
import CompilerDaemon_mod
import string
import CompilerDaemonConfiguration
import tempfile

lock = threading.Lock()
open_sockets = []
# used by init_config()
VERSION = "0.0"

def unregister_connection(socket):
    assert socket in CompilerDaemon_mod.open_sockets
    lock.acquire()
    del CompilerDaemon_mod.open_sockets[CompilerDaemon_mod.open_sockets.index(socket)]
    lock.release()
    
class CompilerDaemon(Daemon):
    
    def __init__(self,\
                 config_file_path,\
                 default_values,\
                 keys_match,\
                 command_line_match):
        Daemon.__init__(self,\
                        config_file_path,\
                        default_values,\
                        keys_match,\
                        command_line_match,\
                        CompilerDaemonConfiguration.check_values)
        os.chdir(self.get_config()["temp_dir"])
        tempfile.tempdir = self.get_config()["temp_dir"]

    def display_usage(self):
        print "DMS version " + VERSION + "."
        print "Copyright(c) 2002 Julien Barbot, Julien Gilli, Antoine Payraud, Pascal Richier.\n"
        print "This is the help of the compiler daemon part of DMS :"
        print "Usage : dmsd [-p|--port=listen_port]"
        print "             [--max-processes=nb_processes]"
        print "             [-f config_file_path]"
        print "             [-h|--help]"
        print "             scheduler_ip_address\n"
        print "-p, --port       makes the compiler daemon listen for requests"
        print "                 coming from compiler client on the supplied port."
        print "--max-processes  accept to handle no more than the supplied number of processes"
        print "                 at the same time."
        print "-f               give the path to the config file"
        print "-h, --help       displays this message.\n"

    def clean_on_exit(self):
        ProtocolUtils.connect_send_close(self.get_config()["scheduler_address"],\
                                         string.atoi(self.get_config()["scheduler_port"]),\
                                         [Protocol.UNSUBSCRIBE_ME])
        try:
            self.__listen_socket.shutdown(0)
        except socket.error:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Error when shutdown socket with Scheduler")
        self.__listen_socket.close()
        for open_socket in CompilerDaemon_mod.open_sockets:
            open_socket.shutdown(0)
        self.remove_lock_file()

    def run(self):
        #FIXME: chdir to a directory specified in a config file,
        # environment variable or whatever suitable
        try:
            os.chdir(self.get_config()["temp_dir"])
        except OSError:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Unable to change directory to : " \
                          + self.get_config()["temp_dir"])
            return 0

        tempfile.tempdir = self.get_config()["temp_dir"]


        if ProtocolUtils.\
               connect_send_close(self.get_config()["scheduler_address"],\
                                  string.atoi(self.get_config()["scheduler_port"]),\
                                  [Protocol.RECORD_ME]) == 1:
            sys.exit(1)
        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #FIXME: incertain hack to avoid error messages because of TIME_WAIT
        self.__listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: 
            self.__listen_socket.bind((Protocol.COMPILER_DAEMON_HOST,\
                                       string.atoi(self.get_config()["port"])))
            self.__listen_socket.listen(5)
        except socket.error:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Unable to listen on socket at port : " \
                          + self.get_config()["port"])
            return 0
        else:
            syslog.syslog(syslog.LOG_NOTICE | syslog.LOG_DAEMON, \
                          "Compiler server listening on "\
                          + str(self.__listen_socket.getsockname()))
            
        while 1:
            connection, address = self.__listen_socket.accept()
            lock.acquire()
            CompilerDaemon_mod.open_sockets.append(connection)
            lock.release()
            handle_client_thread = RemoteJob.RemoteJob(connection,\
                                                       self.get_config()["scheduler_address"],\
                                                       string.atoi(self.get_config()["scheduler_port"]))
            handle_client_thread.start()

if __name__ == "__main__":

    config_file_path = "/etc/dms.cfg"
    # configuration data as a dictionnary
    config_dictionnary = {
        # paths
        "temp_dir" : "/tmp/",
        "lock_file_path" : pwd.getpwnam(pwd.getpwuid(os.getuid())[0])[5] + "/dms.pid",
        # execution context
        "user_privilege" : pwd.getpwuid(os.getuid())[0],
        "max_processes" :  2,
        "port" : str(Protocol.COMPILER_DAEMON_PORT),
        #address
        "scheduler_address" : "192.168.0.1",
        "scheduler_port" : "50008"
        }
    
    configuration_keys_match = [
        ("temp_dir", "paths", "temp_dir"),
        ("lock_file_path", "paths", "lock_file_path"),
        ("user_privilege", "exec", "user_privilege"),
        ("max_processes", "exec", "max_processes"),
        ("port", "exec", "port"),
        ("scheduler_address", "address", "scheduler_address"),
        ("scheduler_port", "address", "scheduler_port")
        ]

    command_line_match = [
        (None, "--max-processes", 0, "max_processes"),
        ("-p", "--port", 0, "port")
        ]


    try:
        compiler_daemon = CompilerDaemon(config_file_path,\
                                         config_dictionnary,\
                                         configuration_keys_match,\
                                         command_line_match)
    except OSError, err:
        print >> sys.stderr, "Unable to chdir to the "\
        + err[1] + " directory, aborting."
        syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                      "Unable to chdir to the " + err[1] \
                      + " directory, aborting.")
        sys.exit(1)

    compiler_daemon.start()
