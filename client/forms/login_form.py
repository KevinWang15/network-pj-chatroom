import _tkinter
import tkinter as tk
from common.transmission.secure_channel import establish_secure_channel_to_server
from tkinter import messagebox


class LoginForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.notification['text'] = "Establishing Secure Connection To Server.."

        def do_login():
            try:
                establish_secure_channel_to_server()
            except ConnectionError:
                messagebox.showerror("出错了", "无法连接到服务器")
                exit()

        master.after(100, do_login)

    def create_widgets(self):
        self.notification = tk.Label(self)
        self.notification["text"] = ""
        self.notification.pack(side="bottom")
