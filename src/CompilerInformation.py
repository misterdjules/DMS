__author__ = "Pascal Richier <dieu9000@hotmail.com>,\
Antoine Payraud <payrau_a@epita.fr>"
__version__ = "0.0"
__date__ = "27 August 2002"

class CompilerInformation:
    """This class contains all informations about Compiler
    performances and addresses."""

    def __init__(self, address, port, perf):
        self.__address = address
        self.__port = port
        self.__perf = perf
        self.__nb_job = 0
        self.__nb_job_done = 0

    def get_ip(self):
        return self.__address
    
    def get_port(self):
        return self.__port

    def inc_nb_job(self):
        self.__nb_job += 1

    def dec_nb_job(self):
        self.__nb_job -= 1

    def set_nb_job(self, value):
        self.__nb_job = value

    def get_nb_job(self):
        return self.__nb_job

    def inc_nb_job_done(self):
        self.__nb_job_done += 1

    def get_nb_job_done(self):
        return self.__nb_job_done
