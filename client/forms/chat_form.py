import _tkinter
import tkinter as tk
from common.transmission.secure_channel import establish_secure_channel_to_server
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
from client.memory import user_list
from client.memory import current_user

import select
import _thread
import datetime


class ChatForm(tk.Frame):
    def refresh_user_list(self):
        self.online_users.delete(0, tk.END)
        for key, value in user_list.items():
            self.online_users.insert(0, value['nickname'])  # + " (" + str(value['id']) + ")")
        return

    def socket_reader(self):
        while True:
            rlist, wlist, xlist = select.select([self.sc.socket], [self.sc.socket], [])

            if (self.should_exit):
                return

            if len(rlist):
                data = self.sc.recv()
                if (data):
                    pprint(data)

                    if (data['type'] == MessageType.on_user_online):
                        user_list[data['parameters']['id']] = data['parameters']
                        self.refresh_user_list()

                    if (data['type'] == MessageType.on_user_offline):
                        del user_list[data['parameters']]
                        self.refresh_user_list()

                    if (data['type'] == MessageType.on_new_message):
                        user = user_list[data['parameters']['user_id']]
                        nickname = user['nickname']
                        user_id = user['id']
                        pprint(int(data['parameters']['time']))
                        time = datetime.datetime.fromtimestamp(
                            int(data['parameters']['time']) / 1000
                        ).strftime('%Y-%m-%d %H:%M:%S')

                        self.chat_box.insert(tk.END, nickname + "   " + time + '\n  ',
                                             ('me' if current_user['id'] == user_id else 'them'))

                        if data['parameters']['message']['type'] == 1:
                            # text message
                            message = data['parameters']['message'][
                                'data']
                            self.chat_box.insert(tk.END, message + '\n', ('message'))
                        elif data['parameters']['message']['type'] == 2:
                            # image message
                            pprint(data['parameters'])

                else:
                    print('服务器已被关闭')
                    # messagebox.showerror("出错了", "服务器已经被关闭")
                    self.master.destroy()

    def __init__(self, sc, master=None):
        super().__init__(master)
        self.pack()
        self.master = master
        self.sc = sc
        master.resizable(width=False, height=False)
        master.geometry('600x500')
        self.create_widgets()
        self.should_exit = False
        self.refresh_user_list()

        _thread.start_new_thread(self.socket_reader, ())

        # self.sc.send(MessageType.set_user_name, nickname)

    def send_message(self, _=None):
        message = self.input_text.get()
        if (not message):
            return
        self.sc.send(MessageType.send_message, {'type': 1, 'data': message})
        self.input_text.set("")
        return 'break'

    def create_widgets(self):
        self.online_users = tk.Listbox(self, height=50, bg='#FFFFF0')
        self.online_users.pack(side="right", padx=(0, 0), pady=(0, 0))

        self.input_text = tk.StringVar()
        self.input_textbox = tk.Entry(self, width=100, textvariable=self.input_text)
        self.input_textbox.pack(side="bottom", padx=(0, 0), pady=(0, 0))
        self.input_textbox.bind("<Return>", self.send_message)

        self.chat_box = tk.Text(self, x=0, y=0, bg='#f6f6f6')
        self.chat_box.pack(side="left", fill='y')
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("me", foreground="green", lmargin1='10', spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", lmargin1='10', spacing1='5')
        self.chat_box.tag_config("message", foreground="black", lmargin1='14', lmargin2='14', spacing1='5')
