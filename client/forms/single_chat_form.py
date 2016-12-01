import tkinter as tk
from tkinter import *

import client.memory
from client.util.socket_listener import *
from tkinter.scrolledtext import ScrolledText


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
        self.append_to_chat_box(data['sender_name'] + "  " + time + '\n  ',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        message = data['message'].replace('\n', '\n  ')
        self.append_to_chat_box(message + '\n', 'message')

    def __init__(self, target_user, master=None):
        super().__init__(master)
        self.master = master
        self.target_user = target_user
        client.memory.unread_message_count[0][self.target_user['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        master.minsize(520, 370)
        self.master.title(target_user['nickname'])

        self.input_frame = tk.Frame(self, bg='white')

        self.input_textbox = ScrolledText(self, height=10)
        self.input_textbox.bind("<Control-Return>", self.send_message)

        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)', command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)

        self.font_btn = tk.Button(self.input_frame, text='修改字体')
        self.font_btn.pack(side=LEFT, expand=False)

        self.image_btn = tk.Button(self.input_frame, text='发送图片')
        self.image_btn.pack(side=LEFT, expand=False)

        self.chat_box = ScrolledText(self, bg='#f6f6f6')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("me", foreground="green", spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", spacing1='5')
        self.chat_box.tag_config("message", foreground="black", spacing1='0')
        self.chat_box.tag_config("system", foreground="grey", spacing1='0',
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
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        pprint(message.strip)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': 0, 'target_id': self.target_user['id'], 'message': message.strip().strip('\n')})
        self.input_textbox.delete("1.0", END)
        return 'break'
