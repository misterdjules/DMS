__author__ = "Julien Gilli"
__version__ = "0.0"
__date__ = "10 August 2002"

import threading
import Protocol
#import CompilerCommand
import FileUtils
import string
import tempfile
import os
import stat
import socket
import popen2
import CompilerDaemon_mod
import ProtocolUtils
import CompilerCommandFactory
import sys
import syslog
    
class RemoteJob(threading.Thread):
    """This class is an abstraction of a remote process.
    It is instanciated by the compiler daemon each time
    it receives a request from a compiler client.
    As now, the remote job is actually always a remote compilation
    job, but it could be anything necessary to handle a client
    request in the future, depending on the comment
    sent by the client.
    """
    # a lock that is shared by all RemoteJob instances
    # in order to prevent the creation of same temporary file names
    tmp_file_creation_lock = threading.Lock()
    nb_job = 0

    def __init__(self, socket, scheduler_address, scheduer_port):
        """The socket argument is the one used
        to communicate with the client that has requested the job"""
        RemoteJob.nb_job += 1
        threading.Thread.__init__(self)
        self.__client_socket = socket
        self.__scheduler_address = scheduler_address
        self.__scheduler_port = scheduer_port
        # Associate a command string as received through the communication
        # channel to the python function to execute if this comand
        # string is received
        self.__commands = {
            Protocol.COMPILE_COMMAND : RemoteJob.compiler_job
            }


    def close_client_connection(self):
        CompilerDaemon_mod.unregister_connection(self.__client_socket)
        try:
            self.__client_socket.close()
        except socket.error:
            pass            

    def run(self):
        """This method is called when the thread is started
        by the compiler daemon.
        The client use the defined protocol to tell the remote
        job what to do. The definition of the protocol is available
        in doc/protocol.txt."""
        
        try:
            command = self.__client_socket.recv(Protocol.COMMAND_TYPE_SIZE)
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, "command received " + command)
            # FIXME: is there another more readable form to perform this call ?
            method_to_call = self.__commands[command]
            method_to_call(self)
        except socket.error:
            pass
        except KeyError:
            syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, "Unknown command received.")
        self.close_client_connection()
        
    def send_exit_code(self, exit_code):
        """Send the exit code "exit_code" of the executed command to the client."""

        self.__client_socket.send(Protocol.EXIT_CODE_COMMAND)
        ProtocolUtils.send_data(self.__client_socket, str(exit_code))

    def set_and_send_nb_job_to_scheduler(self):
        """Send the number of current compilation job running to
        the Scheduler"""
        RemoteJob.nb_job -= 1
        ProtocolUtils.connect_send_close(self.__scheduler_address,\
                                         self.__scheduler_port,\
                                         [Protocol.JOB_DONE, "%s"%(RemoteJob.nb_job)])
        
    def send_output_messages(self, msg_stdout, msg_stderr, input_files,\
                             output_files):
        # replace temporary filenames in messages
        for original_input_file in input_files.keys():
            msg_stdout = msg_stdout.replace(\
                input_files[original_input_file],\
                original_input_file)
            msg_stderr = msg_stderr.replace(\
                input_files[original_input_file],\
                original_input_file)
        # send stdout messages
        ProtocolUtils.send_data(self.__client_socket, msg_stdout)

        # send stderr messages
        ProtocolUtils.send_data(self.__client_socket, msg_stderr)
  
    def send_result_files_back_to_client(\
        self,\
        input_files,\
        output_files):
        """Send the result (output files and output messages) to the client,
        and replace the temporary input file names in the various messages by
        the original ones."""

        #clean temporary input files created
        for tmp_input_file in input_files.values():
            os.unlink(tmp_input_file)
        # FIXME: don't forget to send stdout and stderr
        
        # then send output files back to the client
        for original_output_file_name in output_files.keys():
            self.__client_socket.send(Protocol.FILE_COMMAND)

            ProtocolUtils.send_data(self.__client_socket, original_output_file_name)

            # send the file
            tmp_output_file = open(\
                output_files[original_output_file_name], 'rb')
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, "Sending file : "\
                              + output_files[original_output_file_name])
            ProtocolUtils.send_data(self.__client_socket, tmp_output_file.read())                 
            tmp_output_file.close()
            os.unlink(output_files[original_output_file_name])
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, "File sent : "\
                              + output_files[original_output_file_name])
        
    def compiler_job(self):
        """This method is called when a remote client
        ask a compiler daemon to compile some source code,
        and send it back the results of the compilation
        (object files generally).
        Return 0 if everything has been done without any error,
        and other values otherwise.
        """

        if __debug__:
            print >> sys.stderr, "Execution d'un job de compilation"
        syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,
                      "Launching compilation job.")
        # receive the length of the command line to be received
        compiler_command_line = ProtocolUtils.recv_data(self.__client_socket)
        if __debug__:
            syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,
                          "Compilation command line received : "\
                          + compiler_command_line)
        compiler_command = CompilerCommandFactory.build_compiler_instance\
                           (compiler_command_line.split())


        # get the content of the input files used in the command line we
        # have just received
        input_temp_files = {}
        output_temp_files = {}
        command = self.__client_socket.recv(Protocol.COMMAND_TYPE_SIZE)
                                            
        while command == Protocol.FILE_COMMAND:

            file_name = ProtocolUtils.recv_data(self.__client_socket)

            # FIXME: do we need to create the file inside the
            # critical section ?
            RemoteJob.tmp_file_creation_lock.acquire()
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,\
                              "Creating temporary file.")
            tmp_file_name = tempfile.mktemp(\
                FileUtils.get_file_extension(file_name))
            tmp_file = open(tmp_file_name, 'w')
            RemoteJob.tmp_file_creation_lock.release()
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,\
                              "Temporary file created.")

            input_temp_files[file_name] = tmp_file_name
            tmp_file.write(ProtocolUtils.recv_data(self.__client_socket))
            tmp_file.flush()
            tmp_file.close()
            command = self.__client_socket.recv(Protocol.COMMAND_TYPE_SIZE)
                                                

        # replace original input files in the command line by the
        # temporary ones
        compiler_command.replace_input_files(input_temp_files)
        if __debug__:
            syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, \
                          "New compilation command line :"\
                          + " ".join(compiler_command.get_command_args()))


        # FIXME We should not use "-o" here, this is compiler dependant
        if "-o" in compiler_command.get_command_args():
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, \
                              "-o option in command line.")
            try:
                index_output = compiler_command.get_command_args().index("-o") \
                               + 1
                
                # FIXME: do we need to create the file inside the
                # critical section ?
                RemoteJob.tmp_file_creation_lock.acquire()
                tmp_output_file = tempfile.mktemp()
                tmp_output_file_hdl = open(tmp_output_file, 'w')
                tmp_output_file_hdl.close()
                RemoteJob.tmp_file_creation_lock.release()
                # associate the output tmp file with the original one
                output_file_name = compiler_command.get_command_args()\
                                  [index_output]
                output_temp_files[output_file_name] = tmp_output_file
                # replace the output file name in the command line
                compiler_command.get_command_args(\
                    )[index_output] = tmp_output_file
            except IndexError:
                # if there is no file name after the -o option,
                # it means that the command line is wrong, but we
                # must execute it in order to send the error
                # msg back to the client
                pass
        else:
            # no output file specified with -o switch
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, \
                              "No -o option in command line.")
            for original_input_file_name in input_temp_files.keys():
                stop_step = compiler_command.get_stop_step()
                orig_output_file_name = compiler_command.\
                                        get_output_file_name_for_step(\
                    original_input_file_name,\
                    stop_step)
                output_temp_files[\
                    orig_output_file_name] = compiler_command.\
                    get_output_file_name_for_step(\
                    input_temp_files[original_input_file_name],\
                    stop_step)
                
                if __debug__:
                    syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, \
                                  "File to return to the client : "\
                                  + output_temp_files[orig_output_file_name])
                
        # execute the command in a subshell and get the stdout and stderr output
        if __debug__:
            syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON, \
                          "Executing the following command line : " \
                          + compiler_command.get_local_compiler_path() + " " +\
                          " ".join(compiler_command.get_command_args()[1:]))

        #proc = popen2.Popen3(" ".join(compiler_command.get_command_args()), 1)

        # FIXME : VERY IMPORTANT
        # uncomment the next two line to replace the previous one
        proc = popen2.Popen3(compiler_command.get_local_compiler_path() + " "\
                             + " ".join(compiler_command.get_command_args()[1:]), 1)
        msg_stderr = proc.childerr.read()
        msg_stdout = proc.fromchild.read()
        proc.childerr.close()
        proc.fromchild.close()
        exit_code = proc.wait()

        self.send_output_messages(msg_stdout, msg_stderr, input_temp_files,\
                                  output_temp_files)

        if os.WIFEXITED(exit_code):
            exit_code = os.WEXITSTATUS(exit_code)
        if os.WIFSIGNALED(exit_code):
            exit_code = os.WTERMSIG(exit_code)
        if __debug__:
            syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,\
                          "Exit code : " + str(exit_code))
        if exit_code == 0:
            # send the result (output files and output messages) to the client
            self.send_result_files_back_to_client(input_temp_files,\
                                                  output_temp_files)
            if __debug__:
                syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,\
                              "Output files sent.")
        self.send_exit_code(exit_code)
        self.set_and_send_nb_job_to_scheduler()
