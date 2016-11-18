from pprint import pprint
from common.message import MessageType
from server.memory import socket_mappings
from server.memory import get_online_users
from server.broadcast import broadcast
import time


def run(sc, parameter):
    broadcast(MessageType.on_new_message,
              {"message": parameter, 'user_id': socket_mappings['user_id'][sc.socket], 'time': int(round(time.time() * 1000))})
