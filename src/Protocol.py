__author__ = "Julien Gilli <jgilli@nerim.fr>"
__version__  = "0.0"
__date__ ="11 August 2002"

# port numbers
COMPILER_DAEMON_PORT = 50007
SCHEDULER_DAEMON_PORT = 50008
SCHEDULER_DAEMON_PORT_INFO = 50009

# listen on the machine that instanciate the compiler daemon
COMPILER_DAEMON_HOST =''
SCHEDULER_DAEMON_HOST = ''

COMMAND_TYPE_SIZE = 4
DATA_LENGTH = 8
EXIT_CODE_SIZE = 2

MAX_BROADCAST_SIZE = 1024

# Various client compiler to compiler daemon command codes
FILE_COMMAND = "FILE"
COMPILE_COMMAND = "COMP"
STOP_COMMAND = "STOP"
EXIT_CODE_COMMAND = "EXCO"

# Various client compiler to scheduler deamon command codes
REQUEST_HOST = "REHO"

# Various host compiler to scheduler deamon command codes
RECORD_ME = "HORE"
UNSUBSCRIBE_ME = "UNME"
HOST_FREE = "FREE"
JOB_DONE = "JODO"

# Various monitor to scheduler deamon command codes
REQUEST_INFO = "INFO"
