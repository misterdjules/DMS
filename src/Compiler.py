#!/usr/bin/python -O
__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__ = "0.0"
__date__ = "10 August 2002"

import CompilerCommandFactory
import os.path
import subprocess
import socket
import Protocol
import ProtocolUtils
import Configuration
import CompilerConfiguration

def display_usage():
    print "You shouldn't see this message, if so, please mail someone@somewhere.org."
    print "Indeed, it means that the program is buggy."

class Compiler:
    """This class is the abstraction of the compilation process.
    There is one instance of this class for each compiler command line
    executed by make.
    It uses  the CompilerCommand class, and communicates with
    the scheduler and any compiler daemon the scheduler tell it
    to compile the process on."""
    
        
    def __init__(self, command_args, keys_match, default_values, \
                 command_line_match, config_file_path):
        """command_args are the command line arguments
        including the executable name"""

        self.__compiler_command = CompilerCommandFactory.build_compiler_instance\
                                  (command_args)
        self.__config = Configuration.get_configuration(display_usage,\
                                                        CompilerConfiguration.check_values,
                                                        keys_match,
                                                        default_values,
                                                        command_line_match,
                                                        config_file_path, 0)

    def execute_command(self):
        """This method execute the command line passed as an argument
        to his constructor, either remotely or locally. Return the exit
        code of the command execution."""
        if __debug__:
            print "Is the following command : "\
                  + " ".join(self.__compiler_command.get_command_args())\
                  + " distributable ?"
        if self.__compiler_command.is_distributable():
            preprocessed_files = self.__compiler_command.do_preprocessing_step()
            try:
                exit_code = self.__execute_command_remotely(preprocessed_files)
            except socket.error:
                exit_code = self.__execute_command_locally()
        else:
            exit_code = self.__execute_command_locally()
        return exit_code
            
    def __execute_command_remotely(self, preprocessed_files):
        """Execute the command associated with this compiler instance
        on a remote host and get the results back."""
        if __debug__:
            print >> sys.stderr, "Distant execution of the command : "\
                  + " ".join(self.__compiler_command.get_after_preprocessing_options())

        # here, the scheduler give an hostname to which 
        # we would send the compilation job

        #FIXME: catch exception here
        self.__scheduler_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__scheduler_socket.connect((self.__config['scheduler_address'],
                                         int(self.__config['scheduler_port'])))

        ProtocolUtils.send_data(self.__scheduler_socket, Protocol.REQUEST_HOST)
        compiler_host = ProtocolUtils.recv_data(self.__scheduler_socket)
        self.__scheduler_socket.close()

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # here we connect to the compiler_host
        self.__socket.connect((compiler_host,\
                               Protocol.COMPILER_DAEMON_PORT))
        # ask for a compilation job
        self.__socket.send(Protocol.COMPILE_COMMAND)

        # send the compilation command line

        ProtocolUtils.send_data(self.__socket,
                                " ".join(self.__compiler_command.get_after_preprocessing_options()))

        # send each file along with their name
        if __debug__:
            print >> sys.stderr, "List of files to send : " + str(preprocessed_files)
            
        for (tmp_input_file, input_file_name) in preprocessed_files:
            if __debug__:
                print >> sys.stderr, "Sending of a preprocessed file: %s" % input_file_name
            self.__socket.send(Protocol.FILE_COMMAND)

            # send the file name
            ProtocolUtils.send_data(self.__socket, input_file_name)

            # send the file content
            # FIXME: currently we don't handle file size > 4 Gos
            tmp_input_file.seek(0)
            ProtocolUtils.send_data(self.__socket, tmp_input_file.read())
            tmp_input_file.close()
            
        # unblock the compiler server
        self.__socket.send(Protocol.STOP_COMMAND)
        # get the output messages
        # first stdout, then stderr
        std_out_msg = ProtocolUtils.recv_data(self.__socket)
        if __debug__:
            print >> sys.stderr, "STDOUT message : " + std_out_msg

        std_err_msg = ProtocolUtils.recv_data(self.__socket)
        if __debug__:
            print >> sys.stderr, "STDERR message : " + std_err_msg

        # then get the output files content
        command = self.__socket.recv(Protocol.COMMAND_TYPE_SIZE)
                                     
        while command == Protocol.FILE_COMMAND:
            file_name = ProtocolUtils.recv_data(self.__socket)

            if __debug__:
                print >> sys.stderr, "file name : " + file_name
            #FIXME This is a bad patch to make DMS work well
            # but it have to be really fixed
            # Maybe the CompilerCommands class have to be reworked
            if "-o" in self.__compiler_command.get_command_args():
                file = open(file_name, 'wb')
            else:
                file = open(os.path.basename(file_name), 'wb')

            file.write(ProtocolUtils.recv_data(self.__socket))
            file.flush()
            file.close()

            if __debug__:
                print "File written."
            command = self.__socket.recv(Protocol.COMMAND_TYPE_SIZE)

        assert command == Protocol.EXIT_CODE_COMMAND
        print >> sys.stderr, "Command received : " + command
        # finally get the exit code
        exit_code = int(ProtocolUtils.recv_data(self.__socket))
        if __debug__:
            print "Return code : " + str(exit_code)
        self.__socket.close()
        return exit_code
    
    def __execute_command_locally(self):
        """Execute the command associated with this compiler instance
        on the local host"""
        if __debug__:
            print "Local execution of the following command : "\
                  + " ".join(self.__compiler_command.get_command_args())
        exec_name = self.__compiler_command.get_local_compiler_path()

        exit_status = subprocess.call([exec_name] +
                                      self.__compiler_command.get_command_args()[1:])

        return exit_status
    
if __name__ == "__main__":
    try:
        import sys
        # FIXME: do it in a better way, and check if it works
        # in every case
        sys.argv[0] = os.path.basename(sys.argv[0])
        # FIXME: this prevent DMS to correctly handle such a command line :
        # gcc -DHAVE_CONFIG_H -I. -I. -I../include -DPREFIX=\"/usr\" -g -O2 -Wall
        # -c `test -f session.c || echo './'`session.c
        # where gettext use the PREFIX macro like this :
        # some_function(PREFIX "/trailing/path)
        # It seems that the \" are transformated into ", which leave
        # the above call as : some_function(/usr "/trailing/path") instead
        # of some_function("/usr" "/trailing/path"). 
        for i in range (len(sys.argv)):
            sys.argv[i] = sys.argv[i].replace('"', '\\"')
    finally:
        keys_match = [
            ("scheduler_address", "network", "scheduler_address"),
            ("scheduler_port", "network", "scheduler_port")
            ]

        command_line_match = []

        default_values = {
            "scheduler_address" : "192.168.0.1",
            "scheduler_port" : "50008"
            }

        config_file_path = "/etc/dms-compiler.cfg"
        
        compiler = Compiler(sys.argv, keys_match, default_values, \
                            command_line_match, config_file_path)

        exit_code = compiler.execute_command()
        sys.exit(exit_code)
