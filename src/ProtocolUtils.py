__author__ = "Julien Gilli <jgilli@nerim.fr>,\
Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "24 August 2002"

import socket
import string
import Protocol
import syslog
import sys
#import lzo

def send_data(socket, data):
    """Send data through the connection "socket" """
    # send data size
    #    data = lzo.compress(data, 1)

    size_to_send = len(data)
    
    data_size = ("%x" % size_to_send)[:Protocol.DATA_LENGTH]
    data_size = '0' * (Protocol.DATA_LENGTH - len(data_size)) + data_size
    socket.send(data_size)
    
    # send data
    size_sent_so_far = 0
    while size_sent_so_far < size_to_send:
        size_sent_so_far += socket.send(data[size_sent_so_far:])
        
def recv_data(socket):
    """Receive data via the connection "socket" """
    
    # FIXME: use list to drastically improve performance
    # do something like
    # data = []
    # data.append(recv())
    # return string.join(data, '')
    
    # get the data size
    data_size = string.atoi(socket.recv(Protocol.DATA_LENGTH), 16)
    
    # get the data
    data = ""
    tmp_data = socket.recv(data_size)
    data_received_so_far = len(tmp_data)
    data += tmp_data
    
    while data_received_so_far < data_size:
        tmp_data = socket.recv(data_size - data_received_so_far)
        data_received_so_far += len(tmp_data)
        data += tmp_data

    #    return lzo.decompress(data)
    return data

def connect_send_close(address, port, datas):
    """Initialise a connection, send datas, close the connection"""
    #FIXME: Catch exception here :
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #FIXME: incertain hack to avoid error messages because of TIME_WAIT
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: 
        my_socket.connect((address, port))
    except socket.error:
        syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, \
                      "Unable to connect Scheduler %s:%s"%(address, port))
        return 1
    for data in datas:
        send_data(my_socket, data)
    my_socket.close()
    return 0
