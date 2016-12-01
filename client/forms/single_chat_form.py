import tkinter as tk
from tkinter import *

import client.memory
from client.util.socket_listener import *


class SingleChatForm(tk.Frame):
    def remove_listener_and_close(self):
        remove_message_listener(self.message_listener)
        self.master.destroy()
        if self.target_user['id'] in client.memory.window_instance_single:
            del client.memory.window_instance_single[self.target_user['id']]

    def message_listener(self, data):
        self.digest_message(data)

    def digest_message(self, data):
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.append_to_chat_box(data['sender_name'] + "   " + time + '\n  ',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        message = data['message']
        self.append_to_chat_box(message + '\n', 'message')

    def __init__(self, target_user, master=None):
        super().__init__(master)
        self.master = master
        self.target_user = target_user
        client.memory.unread_message_count[0][self.target_user['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        master.minsize(460, 300)
        self.master.title(target_user['nickname'])

        self.input_text = tk.StringVar()
        self.input_textbox = tk.Entry(self, textvariable=self.input_text)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.input_textbox.bind("<Return>", self.send_message)

        self.chat_box = tk.Text(self, bg='#f6f6f6')
        self.chat_box.pack(side=TOP, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("me", foreground="green", lmargin1='10', spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", lmargin1='10', spacing1='5')
        self.chat_box.tag_config("message", foreground="black", lmargin1='14', lmargin2='14', spacing1='5')
        self.chat_box.tag_config("system", foreground="grey", lmargin1='10', lmargin2='10', spacing1='5',
                                 justify='center',
                                 font=("Times New Roman", 8))

        self.pack(expand=True, fill=BOTH)

        self.sc = client.memory.sc
        add_message_listener(0, self.target_user['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target_user['id'] in client.memory.chat_history[0]:
            for msg in client.memory.chat_history[0][target_user['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')

    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(tk.END, message, tags)
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        message = self.input_text.get()
        if not message:
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': 0, 'target_id': self.target_user['id'], 'message': message})
        self.input_text.set("")
        return 'break'
