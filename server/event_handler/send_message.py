from pprint import pprint
from common.message import MessageType
from server.memory import socket_mappings
from server.memory import user_id_mappings
import server.memory
from server.memory import get_online_users
from server.broadcast import broadcast
import time


def run(sc, parameter):
    sender_user_id = socket_mappings['user_id'][sc.socket]
    message = {"message": parameter, 'user_id': sender_user_id,
               'time': int(round(time.time() * 1000))}
    if parameter['target_user_id'] == '':
        broadcast(MessageType.on_new_message,
                  message)
        # push to chat history
        message['sender_nickname'] = user_id_mappings['nickname'][sender_user_id]
        server.memory.chat_history.append(message)
    else:
        target_user_id = int(parameter['target_user_id'])
        user_id_mappings['sc'][target_user_id].send(MessageType.on_new_message,
                                                    message)
        sc.send(MessageType.on_new_message,
                message)

    if len(server.memory.chat_history) > 30:
        server.memory.chat_history = server.memory.chat_history[len(server.memory.chat_history) - 30:]

    pprint(server.memory.chat_history)
