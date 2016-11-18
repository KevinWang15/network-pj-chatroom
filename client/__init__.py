import _tkinter
import tkinter as tk
from client.forms.login_form import LoginForm
from common.transmission.secure_channel import establish_secure_channel_to_server
from common import message
from pprint import pprint


def run():
    root = tk.Tk()
    LoginForm(master=root)
    root.mainloop()
    # login_form.mainloop()

    try:
        root.destroy()
    except tk.TclError:
        pass
