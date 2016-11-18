#!/usr/bin/env python

import socket
from pprint import pprint

from common.config import get_config
from common.cryptography import crypt
from common.message import MessageType
from common.transmission.secure_channel import accept_client_to_secure_channel
from common.util import long_to_bytes
import select


def run():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(1)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    connections = []
    buffered_output = {}

    s_to_sc = {}

    while True:
        rlist, wlist, xlist = select.select(connections + [s], buffered_output.keys(), [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = accept_client_to_secure_channel(s)
                s_to_sc[sc.socket] = sc
                connections.append(sc.socket)

                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = s_to_sc[i]

            try:
                data = sc.recv()
            except socket.error:
                data = ""

            if data:
                pprint(data)
                sc.send(MessageType.query_room_list, {'ack': 1})

            else:
                # Connection closed
                i.close()
                connections.remove(i)
