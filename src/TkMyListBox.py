from Tkinter import *

class TkMyListBox(Frame):
    def __init__(self,\
                 master,\
                 name,\
                 width,\
                 fg,\
                 bg,\
                 selectforeground,\
                 selectbackground,\
                 yscrollcommand,\
                 exportselection,\
                 selectmode):

        Frame.__init__(self, master)

        self.__label = Label(self, text = name)
        self.__label.pack()

        self.__listbox = Listbox(self,\
                                 width = width,\
                                 fg = fg,\
                                 bg = bg,\
                                 selectforeground = selectforeground,\
                                 selectbackground = selectbackground,\
                                 yscrollcommand = yscrollcommand,\
                                 exportselection = exportselection,\
                                 selectmode = selectmode)
        self.__listbox.pack(padx = 5)

        
    def yview(self, *args):
        apply(self.__listbox.yview, args)

    def curselection(self):
        return self.__listbox.curselection()

    def select_clear(self, *args):
        apply(self.__listbox.select_clear, args)

    def select_set(self, *args):
        apply(self.__listbox.select_set, args)

    def delete(self, *args):
        apply(self.__listbox.delete, args)

    def insert(self, *args):
        apply(self.__listbox.insert, args)

    def bind(self, *args):
        apply(self.__listbox.bind, args)
