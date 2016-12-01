import select
from pprint import pprint
from tkinter import messagebox
from common.message import MessageType
import datetime
import time
import client.memory

callback_funcs = []

# [{target_id,target_type,func}]
message_listeners = []


def gen_last_message(obj):
    # type 0 - 文字消息 1 - 图片消息
    if obj['type'] == 0:
        return obj['data'].replace('\n', ' ')


def socket_listener_thred(sc, tk_root):
    while True:
        rlist, wlist, xlist = select.select([sc.socket], [sc.socket], [])
        if len(rlist):
            data = sc.recv()
            pprint(['new socket data:', data])
            if data:
                # 处理general failure
                if data['type'] == MessageType.general_failure:
                    messagebox.showerror("出错了", data['parameters'])

                # 处理general failure
                if data['type'] == MessageType.server_kick:
                    messagebox.showerror("出错了", '您的账户在别处登入')
                    client.memory.tk_root.destroy()

                # 处理on_new_message
                if data['type'] == MessageType.on_new_message:
                    # time = datetime.datetime.fromtimestamp(
                    #     int(data['parameters']['time']) / 1000
                    # ).strftime('%Y-%m-%d %H:%M:%S')

                    # 放入 chat_history
                    if data['parameters']['target_id'] not in client.memory.chat_history[0]:
                        client.memory.chat_history[0][data['parameters']['target_id']] = []

                    client.memory.chat_history[0][data['parameters']['target_id']].append(data['parameters'])

                    # 更新 last_message
                    client.memory.last_message[0][data['parameters']['target_id']] = gen_last_message(
                        data['parameters']['message'])

                    # 更新 last_message_timestamp
                    client.memory.last_message_timestamp[0][data['parameters']['target_id']] = data['parameters'][
                        'time']

                    # 更新 unread_message_count
                    if data['parameters']['target_id'] not in client.memory.unread_message_count[0]:
                        client.memory.unread_message_count[0][data['parameters']['target_id']] = 0

                    if data['parameters']['target_id'] not in client.memory.window_instance_single:
                        client.memory.unread_message_count[0][data['parameters']['target_id']] += 1

                    # 更新contacts
                    client.memory.contact_window[0].refresh_contacts()

                    # 通知聊天窗口
                    for item in message_listeners:
                        if item['target_type'] == data['parameters']['target_type'] and item['target_id'] == \
                                data['parameters']['target_id']:
                            item['func'](data['parameters'])

                    pprint(client.memory.chat_history)

                for func in callback_funcs:
                    func(data)
            else:
                print('服务器已被关闭')
                # messagebox.showerror("出错了", "服务器已经被关闭")
                tk_root.destroy()


def add_listener(func):
    callback_funcs.append(func)


def remove_listener(func):
    callback_funcs.remove(func)


func_to_tuple = {}


def add_message_listener(target_type, target_id, func):
    func_to_tuple[func] = {'target_type': target_type, 'target_id': target_id, 'func': func}
    message_listeners.append(func_to_tuple[func])


def remove_message_listener(func):
    if func in func_to_tuple:
        message_listeners.remove(func_to_tuple[func])
