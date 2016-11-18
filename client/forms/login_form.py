import _tkinter
import tkinter as tk
from common.transmission.secure_channel import establish_secure_channel_to_server
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
from client.memory import user_list
from client.memory import current_user
from client.forms.chat_form import ChatForm
import select
import _thread
import random


class LoginForm(tk.Frame):
    def socket_reader(self):
        while True:
            rlist, wlist, xlist = select.select([self.sc.socket], [self.sc.socket], [])

            if (self.should_exit):
                return

            if len(rlist):
                data = self.sc.recv()
                if data:
                    pprint(data)
                    if data['type'] == MessageType.set_name_successful:
                        messagebox.showinfo("恭喜", "昵称设置成功, 您的用户ID为：" + str(data['parameters']))
                        current_user['id'] = data['parameters']
                        current_user['nickname'] = self.nickname_text.get()

                    if data['type'] == MessageType.err_nickname_taken:
                        messagebox.showerror("出错了", "昵称已被占用，请换一个")

                    if data['type'] == MessageType.notify_online_user_list:
                        for user in data['parameters']:
                            user_list[user['id']] = user
                        pprint(user_list)
                        ChatForm(self.sc, self.master)
                        self.should_exit = True
                        self.destroy()



                else:
                    print('服务器已被关闭')
                    # messagebox.showerror("出错了", "服务器已经被关闭")
                    self.master.destroy()

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master = master
        master.resizable(width=False, height=False)
        master.geometry('300x140')
        self.create_widgets()
        self.notification['text'] = "Establishing Secure Connection to Server.."
        self.should_exit = False

        def establish_connection():
            try:
                self.sc = establish_secure_channel_to_server()
                self.notification['text'] = "Established Secure Connection to Server"
                self.notification['fg'] = "green"

            except ConnectionError:
                messagebox.showerror("出错了", "无法连接到服务器")
                self.master.destroy()

            _thread.start_new_thread(self.socket_reader, ())

        master.after(100, establish_connection)

    def do_login(self):
        nickname = self.nickname_text.get()
        if (not nickname):
            messagebox.showerror("出错了", "昵称不能为空")
            return
        self.sc.send(MessageType.set_user_name, nickname)

    def create_widgets(self):
        self.notification = tk.Label(self)
        self.notification["text"] = ""
        self.notification.pack(side="bottom", padx=(20, 20), pady=(10, 0))

        self.submit_button = tk.Button(self)
        self.submit_button["text"] = "进入聊天室"
        self.submit_button.pack(side="bottom", padx=(20, 20), pady=(6, 0))
        self.submit_button["command"] = self.do_login

        self.nickname_text = tk.StringVar()
        self.nickname_textbox = tk.Entry(self, width=1000, textvariable=self.nickname_text)
        self.nickname_textbox.pack(side="bottom", padx=(20, 20), pady=(10, 6))

        self.nickname_text.set(
            random.choice(
                ["Jack", "Alan", "Dave", "John", "Peter", "Mary", "Steven", "Alina", "Sam", "Julia", "Mike", "Emily",
                 "Kevin", 'Blake', 'Donald', 'George', 'Frank', 'Gale', 'Harry', 'Justin']))

        self.hint = tk.Label(self)
        self.hint["text"] = "请输入您的昵称:"
        self.hint.pack(side="bottom", padx=(20, 20), pady=(10, 0))
