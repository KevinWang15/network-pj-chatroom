import tkinter as tk
from tkinter import *

import client.memory
from client.util.socket_listener import *
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
import binascii


class ChatForm(tk.Frame):
    font_color = "#000000"
    font_size = 10

    tag_i = 0

    def remove_listener_and_close(self):
        remove_message_listener(self.message_listener)
        self.master.destroy()
        if self.target['id'] in client.memory.window_instance[self.target['type']]:
            del client.memory.window_instance[self.target['type']][self.target['id']]

    def message_listener(self, data):
        self.digest_message(data)

    def digest_message(self, data):
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.append_to_chat_box(data['sender_name'] + "  " + time + '\n  ',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        # type 0 - 文字消息 1 - 图片消息
        if data['message']['type'] == 0:
            self.tag_i += 1
            self.chat_box.tag_config('new' + str(self.tag_i), foreground=data['message']['fontcolor'],
                                     font=(None, data['message']['fontsize']))
            self.append_to_chat_box(data['message']['data'].replace('\n', '\n  ') + '\n', 'new' + str(self.tag_i))
        if data['message']['type'] == 1:
            pprint(['img crc', binascii.crc32(data['message']['data'])])
            client.memory.tk_img_ref.append(ImageTk.PhotoImage(data=data['message']['data']))
            self.chat_box.image_create(END, image=client.memory.tk_img_ref[-1])
            self.append_to_chat_box('\n', '')

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        self.target = target
        client.memory.unread_message_count[self.target['type']][self.target['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=True, height=True)
        master.geometry('660x500')
        master.minsize(520, 370)

        if self.target['type'] == 0:
            self.master.title(self.target['nickname'])

        if self.target['type'] == 1:
            self.master.title("群:" + str(self.target['id']) + " " + self.target['room_name'])

        self.input_frame = tk.Frame(self, bg='white')

        self.input_textbox = ScrolledText(self, height=10)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.input_textbox.bind_all('<Key>', self.apply_font_change)

        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)', command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)

        self.font_btn = tk.Button(self.input_frame, text='字体颜色', command=self.choose_color)
        self.font_btn.pack(side=LEFT, expand=False)

        self.font_btn = tk.Button(self.input_frame, text='字体大小', command=self.choose_font_size)
        self.font_btn.pack(side=LEFT, expand=False)

        self.image_btn = tk.Button(self.input_frame, text='发送图片', command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)

        self.chat_box = ScrolledText(self, bg='white')
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
                                 font=(None, 8))

        self.pack(expand=True, fill=BOTH)

        self.sc = client.memory.sc
        add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target['id'] in client.memory.chat_history[self.target['type']]:
            for msg in client.memory.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')

    def append_to_chat_box(self, message, tags):
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': {
                          'type': 0,
                          'data': message.strip().strip('\n'),
                          'fontsize': self.font_size,
                          'fontcolor': self.font_color
                      }
                      })
        self.input_textbox.delete("1.0", END)
        return 'break'

    def choose_color(self):
        _, self.font_color = colorchooser.askcolor(initialcolor=self.font_color)
        self.apply_font_change(None)

    def choose_font_size(self):
        result = simpledialog.askinteger("设置", "请输入字体大小", initialvalue=self.font_size)
        if result is None:
            return
        self.font_size = result
        self.apply_font_change(None)

    def apply_font_change(self, _):
        try:
            self.input_textbox.tag_config('new', foreground=self.font_color, font=(None, self.font_size))
            self.input_textbox.tag_add('new', '1.0', END)
        except Exception:
            pprint('')

    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.gif;*.png")])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)

            self.sc.send(MessageType.send_message,
                         {'target_type': self.target['type'], 'target_id': self.target['id'],
                          'message': {'type': 1, 'data': b}})
