#!/usr/bin/env python

__author__ = "Pascal Richier <dieu9000@hotmail.com>"
__version__ = "0.0"
__date__ = "16 August 2002"

import socket
import Protocol
import CompilerDistributor
import signal
import os
import sys
import syslog
import Daemon
import pwd
import string
import SchedulerDaemonConfiguration
import SchedulerInfoDistributor

VERSION = "0.0"

class SchedulerDaemon(Daemon.Daemon):
    """This class represent the compiler daemon that distribute the address
    of each accessibles hosts"""

    def __init__(self,\
                 config_file_path,\
                 default_values,\
                 keys_match,\
                 command_line_match):
        Daemon.Daemon.__init__(self,\
                               config_file_path,\
                               default_values,\
                               keys_match,\
                               command_line_match,\
                               SchedulerDaemonConfiguration.check_values)
        
    def display_usage(self):
        print "DMS Scheduler version " + VERSION + "."
        print "Copyright(c) 2002 Julien Barbot, Julien Gilli, Antoine Payraud, Pascal Richier.\n"

    def clean_on_exit(self):
        self.__listen_socket.close()

    def run(self):
        try:
            self.__listen_socket = socket.socket(socket.AF_INET,\
                                                 socket.SOCK_STREAM)
            #FIXME: incertain hack to avoid error messages because of TIME_WAIT
            self.__listen_socket.setsockopt(socket.SOL_SOCKET,\
                                            socket.SO_REUSEADDR,\
                                            1)
            self.__listen_socket.bind((Protocol.SCHEDULER_DAEMON_HOST,\
                                       string.atoi(self.get_config()["port"])))
            self.__listen_socket.listen(5)
        except socket.error:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Unable to listen on socket at port : " \
                          + self.get_config()["port"])
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Exiting dms Scheduler Daemon")
            sys.exit(1)
        else:
            syslog.syslog(syslog.LOG_NOTICE | syslog.LOG_DAEMON, \
                          "Scheduler listening on "\
                          + str(self.__listen_socket.getsockname()))

        infoDistributorThread = SchedulerInfoDistributor.SchedulerInfoDistributor()
        infoDistributorThread.start()
        while 1:
            connection, address = self.__listen_socket.accept()
            handle_client_thread = CompilerDistributor.\
                                   CompilerDistributor(connection,\
                                                       address)
            handle_client_thread.start()

if __name__ == "__main__":

    config_file_path = "/etc/dms-sc.cfg"
    # configuration data as a dictionnary
    config_dictionnary = {
        # paths
        "temp_dir" : "/tmp/",
        "lock_file_path" : pwd.getpwnam(pwd.getpwuid(os.getuid())[0])[5] + "/dms-sc.pid",
        # execution context
        "user_privilege" : pwd.getpwuid(os.getuid())[0],
        "port" : str(Protocol.SCHEDULER_DAEMON_PORT),
        }
    
    configuration_keys_match = [
        ("temp_dir", "paths", "temp_dir"),
        ("lock_file_path", "paths", "lock_file_path"),
        ("user_privilege", "exec", "user_privilege"),
        ("port", "exec", "port"),
        ]

    command_line_match = [
        ("-p", "--port", 0, "port")
        ]


    scheduler_daemon = SchedulerDaemon(config_file_path,\
                                     config_dictionnary,\
                                     configuration_keys_match,\
                                     command_line_match)
    scheduler_daemon.start()
