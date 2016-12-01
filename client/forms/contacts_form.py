import _tkinter
import tkinter as tk
from distutils import command
from tkinter import messagebox
from common.message import MessageType
from pprint import pprint
import client.memory
import select
import _thread
from tkinter import *
from client.components.vertical_scrolled_frame import VerticalScrolledFrame
from client.components.contact_item import ContactItem
from client.forms.single_chat_form import SingleChatForm
from tkinter import Toplevel
import datetime
import client.util.socket_listener
import time
from tkinter import simpledialog


class ContactsForm(tk.Frame):
    def remove_socket_listener_and_close(self):
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        client.memory.tk_root.destroy()

    def socket_listener(self, data):
        if data['type'] == MessageType.incoming_friend_request:
            result = messagebox.askyesnocancel("好友请求", data['parameters']['nickname'] + "请求加您为好友，是否同意？(按Cancel为下次再询问)");
            if result == None:
                return
            self.sc.send(MessageType.resolve_friend_request, [data['parameters']['id'], result])

        if data['type'] == MessageType.contact_info:
            data['parameters']['last_timestamp'] = 0
            data['parameters']['last_message'] = '(没有消息)'
            self.contacts.insert(0, data['parameters'])
            self.refresh_contacts()
            return

        if data['type'] == MessageType.add_friend_result:
            if data['parameters'][0]:
                messagebox.showinfo('添加好友', '好友请求已发送')
            else:
                messagebox.showerror('添加好友失败', data['parameters'][1])
            return

        if data['type'] == MessageType.friend_on_off_line:
            friend_user_id = data['parameters'][1]

            for i in range(0, len(self.contacts)):
                if self.contacts[i]['id'] == friend_user_id:
                    self.contacts[i]['online'] = data['parameters'][0]
                    break

            self.refresh_contacts()
            return

    def on_frame_click(self, e):
        user_id = e.widget.user['id']
        if user_id in client.memory.window_instance_single:
            # pprint(client.memory.window_instance_single[user_id])
            client.memory.window_instance_single[user_id].master.deiconify()
            return
        form = Toplevel(client.memory.tk_root, takefocus=True)
        client.memory.window_instance_single[user_id] = SingleChatForm(e.widget.user, form)

    def on_add_friend(self):
        result = simpledialog.askstring('添加好友', '请输入用户名')
        if (not result):
            return
        self.sc.send(MessageType.add_friend, result)

    def on_add_room(self):
        pprint('11')

    pack_objs = []

    def refresh_contacts(self):
        def compare(item1, item2):
            ts1 = client.memory.last_message_timestamp[item1['type']].get(item1['id'], 0)
            ts2 = client.memory.last_message_timestamp[item2['type']].get(item2['id'], 0)
            if ts1 < ts2:
                return -1
            elif ts1 > ts2:
                return 1
            else:
                return 0

        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()

        self.pack_objs = []

        # sorted(self.contacts, cmp=compare)
        self.contacts.sort(key=lambda x: -client.memory.last_message_timestamp[x['type']].get(x['id'], 0))
        for item in self.contacts:
            contact = ContactItem(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.user = item

            contact.bind("<Button>", self.on_frame_click)
            contact.title.config(text=item['nickname'] + (' (在线)' if item['online'] else ' (离线)'))
            contact.title.config(fg='green' if item['online'] else '#999')

            # contact.last_message.config(text=item['nickname'] + (' (在线)' if item['online'] else ' (离线)'))

            self.pack_objs.append(contact)
            time_message = datetime.datetime.fromtimestamp(
                item['last_timestamp']
            ).strftime('%Y-%m-%d %H:%M:%S')

            contact.last_message_time.config(text=time_message)

            contact.last_message.config(text=client.memory.last_message[item['type']].get(item['id'], '(没有消息)'))
            contact.last_message_time.config(text=datetime.datetime.fromtimestamp(
                int(client.memory.last_message_timestamp[item['type']].get(item['id'], 0)) / 1000
            ).strftime('%Y-%m-%d %H:%M:%S'))

            unread_count = client.memory.unread_message_count[item['type']].get(item['id'], 0)
            contact.unread_message_count.pack_forget()
            if unread_count != 0:
                contact.last_message.pack_forget()
                contact.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
                contact.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
                contact.unread_message_count.config(text=str(unread_count))

    def __init__(self, master=None):
        client.memory.contact_window.append(self)
        super().__init__(master)
        self.master = master
        screen_width = client.memory.tk_root.winfo_screenwidth()
        screen_height = client.memory.tk_root.winfo_screenheight()
        x = screen_width - 300
        y = (screen_height / 2) - 400
        master.geometry('%dx%d+%d+%d' % (260, 600, x, y))
        self.scroll = VerticalScrolledFrame(self)
        self.scroll.pack(fill=BOTH, expand=True)
        self.pack(side=TOP, fill=BOTH, expand=True)

        self.button_frame = Frame(self)

        self.add_friend = Button(self.button_frame, text="添加好友", command=self.on_add_friend)
        self.add_friend.pack(side=LEFT, expand=True, fill=X)

        self.add_room = Button(self.button_frame, text="添加群", command=self.on_add_room)
        self.add_room.pack(side=LEFT, expand=True, fill=X)

        self.button_frame.pack(expand=False, fill=X)

        self.contacts = []

        # for i in range(0, 60):
        #     contact = ContactItem(self.scroll.interior)
        #     contact.pack(fill=BOTH, expand=True)
        #     contact.bind("<Button>", self.on_frame_click)

        self.master.title(client.memory.current_user['nickname'] + " - 联系人列表")
        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)
