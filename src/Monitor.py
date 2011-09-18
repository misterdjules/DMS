#!/usr/bin/env python

__author__ = "Pascal Richier <dieu9000@hotmail.com>"
__version__ = "0.0"
__date__ = "16 September 2002"

from Tkinter import *
from Dialog import *
import TkTable
import MonitorHelp
import Protocol
import socket
import string
import Configuration
import MonitorConfiguration
import MonitorRefresh
import Protocol

class Monitor(Frame):
    
    def __init__(self,\
              config_file_path,\
              default_values,\
              keys_match,\
              command_line_match):
        """Create an instance of the monitor."""
        Frame.__init__(self)

        self.__config = Configuration.get_configuration(self.display_usage,\
                                                        MonitorConfiguration. check_values,\
                                                        keys_match,\
                                                        default_values,\
                                                        command_line_match,\
                                                        config_file_path)

    
        self.gData = None
        self.gMaj = 0
        self.gInCom = 1
        self.gLock = 1
        
        self.__table_selected_line = 0
        self.__refresh_ability = 1
        self.__showing_help = 0
        self.__refresh_func_count = 0
        self.colonnes = [("IP", 12),\
                         ("Port", 5),\
                         ("Jobs done",7)]

        self.pack(expand=YES, fill=BOTH)
        self.master.title('DMS - Monitor')
        self.master.iconname('dmsM')

        ftitre = Frame(self)
        ftitre.pack(pady=10)
        self.ltitle = Label(ftitre)
        self.ltitle["relief"] = "groove"
        self.ltitle["borderwidth"] = 5
        self.ltitle["text"] ='DMS - Monitor'
        self.ltitle["background"] = 'Grey'
        self.ltitle["foreground"] = 'blue'
        self.ltitle["width"] = 20
        self.ltitle["height"] = 3
        self.ltitle.pack()
        self.ltitre_ip = Label(ftitre,
                               text = "ip : %s"%(self.__config["scheduler_address"])).pack()
        self.ltitle_port = Label(ftitre, text = "port : %s"%(Protocol.SCHEDULER_DAEMON_PORT_INFO)).pack()

        fpresentation = Frame(self)
        fpresentation.pack(pady=10)
        self.presentationHost = Label(fpresentation)
        self.presentationHost["text"] ="Hosts (full/active/idle) : _/_/_"
        self.presentationHost.pack()
        self.presentationJobs = Label(fpresentation)
        self.presentationJobs["text"] ="Jobs (full/done/working) : _/_/_"
        self.presentationJobs.pack()

        self.ftable = TkTable.TkTable(self,\
                                 [("IP", 16),\
                                  ("Port", 5),\
                                  ("Jobs",3),\
                                  ("Jobs done",7)])
        self.ftable.pack(pady=10)
        self.ftable.listbox_list_set({"IP":[],\
                                      "Port":[],\
                                      "Jobs":[],\
                                      "Jobs done":[]})

        fcontrole = Frame(self)
        fcontrole.pack(pady=10)
        
        f_scale_refresh = Frame(fcontrole)
        f_scale_refresh.pack(pady = 10,\
                             padx = 25,\
                             side = LEFT)
        
        self.scale_refresh = Scale(f_scale_refresh,\
                                   orient=HORIZONTAL,\
                                   from_ = 1,\
                                   to = 256,\
                                   command = self.scale_chg)
        self.scale_refresh.set(1)
        self.scale_refresh.pack()
        Label(f_scale_refresh,text="Refresh periode").pack()
        Label(f_scale_refresh,text="for all (in sec)").pack()
        
        f_buttons_refresh = Frame(fcontrole)
        f_buttons_refresh.pack(pady = 10,\
                               padx = 25,\
                               side = LEFT)

        refrech_method = StringVar()
        check_refrech_method = Checkbutton(f_buttons_refresh,\
                                           text = "only selected",\
                                           variable = refrech_method,\
                                           onvalue = "selected",\
                                           offvalue = "all",\
                                           selectcolor = "green")
        Button(f_buttons_refresh,\
               text='Refresh',\
               command = self.refresh_by_button).pack(padx=3)
        
        f_buttons_apply = Frame(fcontrole)
        f_buttons_apply.pack(pady = 10,\
                               padx = 25,\
                               side = LEFT)
        
        Button(f_buttons_apply,\
               text = 'Help',\
               command = self.print_help).pack(side = LEFT, padx = 3)
        Button(f_buttons_apply,\
               text = 'Quit',\
               command = self.confirm_quit).pack(side = LEFT, padx = 3)

        self.monitor_refresh_thread = MonitorRefresh.\
                                      MonitorRefresh(self,
                                                     self.__config,)


        self.monitor_refresh_thread.start()

        self.refresh()

    def set_title_color(self, color):
        self.ltitle["foreground"] = color

    def get_title_color(self):
        return self.ltitle["foreground"]

    def refresh(self):
        if self.gInCom == 1:
            if self.get_title_color() != "red":
                self.set_title_color("Red")
            self.monitor_refresh_thread.send_info_query()
        else:
            if self.get_title_color() != "#007700":
                self.set_title_color("#007700")
            
        if self.gMaj == 1:
            if self.ltitle["foreground"] != "#007700":
                self.set_title_color("#007700")
            data = self.gData
            self.gMaj = 0
            ip_list = []
            port_list = []
            nb_jobs_list = []
            nb_jobs_done_list = []
            nb_infos = 4
            valid = 0
            host_full = 0
            host_idle = 0
            jobs_full = 0
            jobs_work = 0
            
            info_list = string.split(data, "/")
            if info_list[0] == "info":
                valid = 1
                try:
                    jobs_full = string.atoi(info_list[1], 10)
                except:
                    valid = 0
                for info in info_list[2:]:
                    one_comp = string.split(info, ";")
                    if len(one_comp) != nb_infos:
                        valid = 0
                    if valid == 1:
                        ip_list.append(one_comp[0])
                        port_list.append(one_comp[1])
                        nb_jobs_list.append(one_comp[2])
                        nb_jobs_done_list.append(one_comp[3])
                        host_full += 1
                        try:
                            tmpJobs = string.atoi(one_comp[2], 10)
                        except:
                            valid = 0
                        else:
                            if tmpJobs == 0:
                                host_idle += 1
                            else:
                                jobs_work += tmpJobs
                                
            if valid == 1:
                host_full = len(ip_list)
                self.ftable.listbox_list_set({"IP":ip_list,\
                                              "Port":port_list,\
                                              "Jobs":nb_jobs_list,\
                                              "Jobs done":nb_jobs_done_list})
                self.presentationHost["text"] ="Hosts (full/active/idle) : %s/%s/%s"\
                                                %(host_full,
                                                  host_full - host_idle,
                                                  host_idle)
                self.presentationJobs["text"] ="Jobs (full/done/working) : %s/%s/%s"\
                                                %(jobs_full,
                                                  jobs_full - jobs_work,
                                                  jobs_work)
        self.after(200, self.refresh)

    def display_usage(self):
        print "DMS Monitor version " + VERSION + "."
        print "Copyright(c) 2002 Julien Barbot, Julien Gilli, Antoine Payraud, Pascal Richier.\n"
        print "This is the help of the Monitor part of DMS :"
        print "Usage : monitor.py [-a|--address=listen_scheduler_address_to_contact]"
        print "                   [-h|--help]"
        print "                   scheduler_ip_address\n"
        print "-a, --address  set the Scheduler daemon address to requests\n"
        print "-h, --help     displays this message.\n" 

    def confirm_quit(self):
        d = Dialog(None, title="Goodbye?",
                   text="Really Leave?", default=0,
                   bitmap=DIALOG_ICON, strings=("Yes","No"))
        if d.num == 0:
            self.monitor_refresh_thread.stop_loop()
            self.quit()
        return

    def print_help(self):
        if self.__showing_help == 0:
            self.__showing_help = 1
            toplev_help = MonitorHelp.Help(self)
            self.__showing_help = 0
            
    def scale_chg(self, event = None):
        self.__refresh_func_count += 1
        if self.__refresh_func_count == 1000:
            self.__refresh_func_count = 0
        self.request_info(self.__refresh_func_count)

    def refresh_reativation(self):
        self.__refresh_ability = 1

    def refresh_by_button(self, event = None):
        self.gLock = 0
        

    def request_info(self, refresh_func_count):
        if refresh_func_count != self.__refresh_func_count:
            return
        if self.__refresh_ability == 0:
            self.after(self.scale_refresh.get() * 1000,
                       self.request_info,
                       refresh_func_count)
            return

        self.gLock = 0
        self.__refresh_ability = 0
        self.after(1000, self.refresh_reativation)
        
        self.after(self.scale_refresh.get() * 1000,
                   self.request_info,
                   refresh_func_count)
        
if __name__ == "__main__":

    config_file_path = "/etc/dms-mo.cfg"
    # configuration data as a dictionnary
    config_dictionnary = {
        "scheduler_address" : "127.0.0.1"
        }
    
    configuration_keys_match = [
        ("scheduler_address", "com", "scheduler_address")
        ]

    command_line_match = [
        ("-a", "--address", 0, "scheduler_address")
        ]
    monitor = Monitor(config_file_path,\
                      config_dictionnary,\
                      configuration_keys_match,\
                      command_line_match)

    monitor.mainloop()
