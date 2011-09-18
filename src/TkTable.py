import TkMyListBox
from Tkinter import *
import string

class TkTable(Frame):
    def __init__(self, master, name_width_list):

        Frame.__init__(self, master)
        
        self.__scrollbar = Scrollbar(self, orient=VERTICAL)
        self.__scrollbar.pack(side=LEFT, fill=Y)
        self.__scrollbar.config(command=self.yview)
        
        self.__listbox_map = {}

        for name, width in name_width_list:
            self.__listbox_map[name] = \
                                     TkMyListBox.TkMyListBox(self,\
                                                         name,\
                                                         width,\
                                                         "#00AA00",\
                                                         "black",\
                                                         "white",\
                                                           "#0000AA",\
                                                         self.__scrollbar.set,\
                                                         0,\
                                                         "single")
            self.__listbox_map[name].pack(side=LEFT)
            self.__listbox_map[name].insert(END, name)
            self.__listbox_map[name].select_set(0)
            self.__listbox_map[name].bind('<<ListboxSelect>>', self.poll)
            self.__listbox_map[name].bind('<MouseWheel>', self.poll)
        
            
        self.__current = ('0',)
        
    def yview(self, *args):
        for name in self.__listbox_map.keys():
            apply(self.__listbox_map[name].yview, args)
        
    def poll(self, event):
        action = 0
        for name in self.__listbox_map.keys():
            cursel = self.__listbox_map[name].curselection()
            if cursel != self.__current:
                self.__current = now = cursel
                action = 1
                break
        if action == 1:
            for name in self.__listbox_map.keys():
                self.__listbox_map[name].select_clear(0, END)
                self.__listbox_map[name].select_set(now)

    def listbox_list_set(self, map_of_list_value):
        for name in self.__listbox_map.keys():      
            self.__listbox_map[name].delete(0, END)
            for value in map_of_list_value[name]:
                self.__listbox_map[name].insert(END, value)
            (a,) =  self.__current
            if (string.atoi(a) > len(map_of_list_value[name])):
                self.__listbox_map[name].select_set(0)
                self.__current = ('0',)
            else:
                self.__listbox_map[name].select_set(self.__current)
