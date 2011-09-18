import os
import sys
import signal
import syslog
import posix
import Configuration
import pwd

__author__ = "Julien Gilli <jgilli@nerim.fr>,\
Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "11 August 2002"


class MustImplementMethod:
    pass

class Daemon:

    def set_config(self, config):
        self.__config = config

    def get_config(self):
        return self.__config
    
    def remove_lock_file(self):
        try:
            os.unlink(self.__config["lock_file_path"])
        except OSError:
            syslog.syslog(syslog.LOG_DAEMON | syslog.LOG_ERR, \
                          "Unable to delete temporary lock file : "\
                          + self.__config["lock_file_path"])
        
    def hangup_handler(self, signum, frame):
        self.clean_on_exit()
        syslog.syslog(syslog.LOG_DEBUG | syslog.LOG_DAEMON,\
                      "Execution de : " + self.__absolute_path)
        try:
            self.remove_lock_file()
            os.execv(self.__absolute_path, sys.argv)
        except OSError:
            syslog.syslog(LOG_ERR | LOG_DAEMON, \
                          "Can't execv, restart failed, exiting.")
            sys.exit(1)
    
    def term_handler(self, signum, frame):
        self.clean_on_exit()
        self.remove_lock_file()
        syslog.syslog(syslog.LOG_NOTICE | syslog.LOG_DAEMON,\
                      "DMS daemon exiting.")
        sys.exit(0)
    def set_lock_file(self):
        # Test if there is already a daemon running
        try:
            lock_file = os.open(self.__config["lock_file_path"],\
                                (os.O_CREAT | os.O_EXCL | os.O_RDWR))
            os.write(lock_file, str(os.getpid()))

        except OSError:
            print >> sys.stderr, "Can't set lock file."
            raise    

    def change_privileges(self):
        try:
            user = pwd.getpwnam(self.__config["user_privilege"])
            os.setreuid(user[2], user[2])
        except KeyError:
            print >> sys.stderr, "User : " + self.__config["user_privilege"]\
                  + " doesn't exist."
            raise OSError
        except OSError:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Can't change user privileges.")
            raise

    def __init__(self,\
                 config_file_path,\
                 default_values,\
                 keys_match,\
                 command_line_match,
                 check_values):
        
        self.__config = self.init_config(config_file_path,\
                                         default_values,\
                                         keys_match,\
                                         command_line_match,
                                         check_values)

        self.__absolute_path = os.path.abspath(sys.argv[0])
        #Add the current directory to the PYTHONPATH
        sys.path.append(os.getcwd())


    def daemonize(self):
        """Makes the program into a daemon."""
        if (os.access(self.__config["lock_file_path"], os.F_OK)):
            print >> sys.stderr, "Daemon already started, exiting."
            sys.exit(1)
            return 0
        
        signal.signal(signal.SIGHUP, self.hangup_handler)
        signal.signal(signal.SIGTERM, self.term_handler)
        
        # Detach the daemon from the controlling terminal
        try:
            pid = os.fork()
        except os.error:
            return 0
        if pid:
            sys.exit(0)
        else:
            self.change_privileges()
            self.set_lock_file()
            posix.setsid()

        self.change_privileges()
        #FIXME: chdir to the root directory, to prevent weird
        #behavior if the directory where the program is stored is no longer available
        try:
            os.chdir("/")
        except OSError:
            syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                          "Unable to change directory to : " \
                          + "/")
            return 0

        # avoid a too permisive umask if the daemon is run as root
        os.umask(027)
    
        # close all file descriptors inherited from the father
        try:
            import resource
            try:
                resource_id = resource.RLIMIT_NOFILE
            except NameError:
                resource_id = resource.RLIMIT_OFILE
                            
                fds_soft, fds_hard = resource.getrlimit(resource_id)
                # Under python, the close function raises OSError
                # upon failure (because here we try to close an unopened fd)
                for fd_soft in range(fds_soft):
                    if fd_soft == 2: continue
                    try:
                        os.close(fd_soft)
                    except OSError:
                        pass
        except ImportError:
            try:
                max_open_files = os.sysconf('SC_OPEN_MAX')
            except OSError:
                max_open_files = 0
            for fd in range(max_open_files):
                try:
                    os.close(fd)
                except OSError:
                    pass
        try:        
            sys.stdin = open('/dev/null', 'r')
            sys.stdout = open('/dev/null', 'w')
            #sys.stderr = open('/dev/null', 'w')
        except OSError:
            syslog.syslog(syslog.LOG_WARNING | LOG_DAEMON, \
                          "Can't redirect standard streams to /dev/null.")
            return 0

    def start(self):
        try:
            if self.daemonize() == 0:
                print >> sys.stderr, "Error, unable to enter daemon mode."
                self.remove_lock_file()
                sys.exit(1)
            self.run()
        # Here, we have to catch SystemExit because the sys.exit() fonction raise the
        # SystemExit exception. And as the father process calls it, we must catch.
        except SystemExit:
            sys.exit(0)
        ##      except:
        ##          print >> sys.stderr, "Errors encountered, exiting."

    def display_usage(self):
        """This method display the usage of the daemon command line.
        Example :
        print "DMS version " + VERSION + "."
        print "Copyright(c) 2002 Julien Barbot, Julien Gilli, Antoine Payraud"
        print "and Pascal Richier."
        print "This is the help of the compiler daemon part of DMS :"
        print "Usage : dmsd [-p|--port=listen_port]"
        """
        raise MustImplementMethod

    def clean_on_exit(self):
        """This method must clean all resources used by the daemon when it terminates, e.g,
        close open files, sockets, etc."""
        raise MustImplementMethod

    def init_config(self, \
                    config_file_path,\
                    default_values,\
                    keys_match,\
                    command_line_match,
                    check_values):
        
        """Init config takes the following argument :
        - config_file_path : the path to the config file , e.g /etc/dms.cfg;
        - default_values : a dictionnary that associate config file keys with their default values, e.g
        {"max_processes" : 2, "connection_port" : 1025}. Here, the configuration file might
        looks like :
        max_processes=6
        connection_port=1025.
        - keys_match associate a key of the config file belonging to a section of the same file with a key
        of the dictionnary. If you want your config file to have a key named max_processes_in_cfg belonging
        to a section named exec and want the value to be associated in the config dictionnary to the
        key "max_processes_in_dict", it should be :
        [("max_procecesses_in_dict", "exec", "max_processes_in_cfg")] .
        - command_line_match : Associate short and long command line option with a type and a the dictionnary
        key which will be affected.
        For example :
        [(None, "--max-processes", 0, "max_processes_in_dict"),
        ("-p", "--port", 0, "port_in_dict"),
        (None, "--status", 1, "display_status_in_dict")
        ]
        The first element of the tuple is the short option, the second is the long option,
        the third is the type of the option :        - 0 means that it expects a value
        - 1 means that it doesn't expect a value, but that the value in the dictionnary is set to
        1 or 0 wether the option is used or not.
        The last element of the tuple is the configuration dictionnary key affected.
        """
        
        
        return Configuration.get_configuration(self.display_usage,\
                                               check_values,\
                                               keys_match,\
                                               default_values,\
                                               command_line_match,\
                                               config_file_path)

    def run():
        """This method must be overriden and must include the logic
        of the daemon."""
        raise MustImplementMethod
