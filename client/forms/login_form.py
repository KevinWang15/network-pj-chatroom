import _tkinter
import tkinter as tk
from common.transmission.secure_channel import establish_secure_channel_to_server
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
import select
import _thread


class LoginForm(tk.Frame):
    def socket_reader(self):
        while True:
            rlist, wlist, xlist = select.select([self.sc.socket], [self.sc.socket], [])
            if len(rlist):
                pprint(self.sc.recv())

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.notification['text'] = "Establishing Secure Connection To Server.."
        self.sc = object

        def do_login():
            try:
                self.sc = establish_secure_channel_to_server()

            except ConnectionError:
                messagebox.showerror("出错了", "无法连接到服务器")
                exit()

            _thread.start_new_thread(self.socket_reader, ())

        def send_message():
            self.sc.send(MessageType.query_room_list, {"a": 1})

        master.after(100, do_login)
        master.after(1000, send_message)
        master.after(3000, send_message)
        master.after(5000, send_message)

    def create_widgets(self):
        self.notification = tk.Label(self)
        self.notification["text"] = ""
        self.notification.pack(side="bottom")
