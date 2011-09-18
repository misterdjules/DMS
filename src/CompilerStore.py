__author__ = "Pascal Richier <dieu9000@hotmail.com>,\
Antoine Payraud <payrau_a@epita.fr>"
__version__ = "0.0"
__date__ = "28 August 2002"

import CompilerInformation
import threading
import syslog
    
class CompilerStore:
    """This class contains all CompilerInformation class
    and perform methode to calculate the optimal host
    to give to the client"""

    __lock = threading.Lock()

    #FIXME: remove this variable
    tmp_nb_tot_job = [0]
    
    def __init__(self):
        self.store = {}

    def record_host(self, address, port, perf):
        new_compiler = CompilerInformation.\
                       CompilerInformation(address,\
                                           port,\
                                           perf)
        self.store[address] = new_compiler

    def remove_host(self, address):
        del self.store[address]

    def give_host(self):
        i = 0
        gived_host = self.store[self.store.keys()[0]]
        self.__lock.acquire()
        if __debug__:
            print self.store
        for host in self.store.keys()[0:]:
            host_i = self.store[host]
            if host_i.get_nb_job() == 0:
                gived_host = host_i
                break
            if host_i.get_nb_job() < gived_host.get_nb_job():
                gived_host = host_i
        gived_host.inc_nb_job()
        self.tmp_nb_tot_job[0] += 1
        self.__lock.release()
        for host in self.store.keys():
            syslog.syslog(syslog.LOG_NOTICE | syslog.LOG_DAEMON, \
                          "host -|"\
                          + host\
                          + "|- with %s || Total now : %s"\
                          %(self.store[host].get_nb_job(),\
                            self.tmp_nb_tot_job[0]))
        return gived_host.get_ip()
        
    def set_nb_job_and_inc_count(self, address, nb_job):
        self.store[address].set_nb_job(nb_job)
        self.store[address].inc_nb_job_done()

    def get_info(self, host = None):
        info = "info/%s"%(self.tmp_nb_tot_job[0])
        for host in self.store.keys():
            host_i = self.store[host]
            info += "/"\
                    + host_i.get_ip()\
                    + ";"\
                    + str(host_i.get_port())\
                    + ";"\
                    + str(host_i.get_nb_job())\
                    + ";"\
                    + str(host_i.get_nb_job_done())
        return info
