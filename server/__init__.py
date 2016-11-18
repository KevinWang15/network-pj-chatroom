#!/usr/bin/env python

import socket
from pprint import pprint

from common.config import get_config
from common.cryptography import crypt
from common.message import MessageType
from common.transmission.secure_channel import accept_client_to_secure_channel
from common.util import long_to_bytes


def run():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(1)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    sc = accept_client_to_secure_channel(s)

    pprint(sc.recv())
    sc.send(MessageType.query_room_list)

    pprint(sc.recv())
    sc.send(MessageType.query_room_list, {"b": 2})

    pprint(sc.recv())
