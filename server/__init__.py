#!/usr/bin/env python
import socket
from common.config import get_config
from common.transmission.secure_channel import accept_client_to_secure_channel
from server.event_handler import handle_event
from server.memory import *
import server.memory
from common.message import MessageType
from server.broadcast import broadcast
import select
from server.util import database
from pprint import pprint


def run():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(1)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    while True:
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = accept_client_to_secure_channel(s)
                socket_to_sc[sc.socket] = sc
                scs.append(sc)
                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = socket_to_sc[i]
            pprint(sc)

            try:
                data = sc.recv()
            except socket.error:
                data = ""

            if data:
                handle_event(sc, data['type'], data['parameters'])

            else:
                # Connection closed
                sc.close()

                # 通知他的好友他下线了
                if sc in sc_to_user_id:
                    user_id = sc_to_user_id[sc]
                    frs = database.get_friends(user_id)
                    for fr in frs:
                        if fr['id'] in user_id_to_sc:
                            user_id_to_sc[fr['id']].send(MessageType.friend_on_off_line, [False, user_id])

                # 把他的连接信息移除
                remove_sc_from_socket_mapping(sc)
