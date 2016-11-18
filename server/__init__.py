#!/usr/bin/env python
import socket
from common.config import get_config
from common.transmission.secure_channel import accept_client_to_secure_channel
from server.event_handler import handle_event
from server.memory import socket_mappings, remove_from_socket_mapping, connections
import server.memory
from common.message import MessageType
from server.broadcast import broadcast
import select


def run():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(1)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    while True:
        rlist, wlist, xlist = select.select(connections + [s], [], [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = accept_client_to_secure_channel(s)
                socket_mappings['sc'][sc.socket] = sc
                socket_mappings['user_id'][sc.socket] = server.memory.user_id_incr
                server.memory.user_id_incr += 1
                connections.append(sc.socket)

                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = socket_mappings['sc'][i]

            try:
                data = sc.recv()
            except socket.error:
                data = ""

            if data:
                handle_event(sc, data['type'], data['parameters'])

            else:
                # Connection closed
                i.close()
                connections.remove(i)
                broadcast(MessageType.on_user_offline, socket_mappings['user_id'][i])
                remove_from_socket_mapping(i)
