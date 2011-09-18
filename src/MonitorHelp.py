from Tkinter import *

class Help(Toplevel):
    def __init__(self,master):
        
        Toplevel.__init__(self,master)

        self.__master = master

        Label(self, text="           help           ").pack()

        self.bind("<Escape>", self.cancel)

        self.wait_window(self)

    def cancel(self,event=None):
        self.destroy()
