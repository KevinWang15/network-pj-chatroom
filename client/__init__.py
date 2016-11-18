import _tkinter
import tkinter as tk
from client.forms.login_form import LoginForm
from common.transmission.secure_channel import establish_secure_channel_to_server
import bson
from gevent import monkey, socket

monkey.patch_all()
bson.patch_socket()


def run():
    root = tk.Tk()

    login_form = LoginForm(master=root)
    login_form.mainloop()

    try:
        root.destroy()
    except tk.TclError:
        pass
