from pprint import pprint
from common.message import MessageType
from server.memory import socket_mappings
from server.memory import user_id_mappings
from server.memory import get_online_users
from server.broadcast import broadcast
import server.memory


def run(sc, parameter):
    # 如果昵称已经被占用，提醒用户换一个
    for key, value in socket_mappings['nickname'].items():
        if value == parameter:
            sc.send(MessageType.err_nickname_taken)
            return

    socket_mappings['nickname'][sc.socket] = parameter
    user_id_mappings['sc'][socket_mappings['user_id'][sc.socket]] = sc
    user_id_mappings['nickname'][socket_mappings['user_id'][sc.socket]] = parameter
    sc.send(MessageType.set_name_successful, socket_mappings['user_id'][sc.socket])
    sc.send(MessageType.notify_online_user_list, get_online_users())
    sc.send(MessageType.server_notification, '欢迎来到聊天室，在下方输入文字，按Enter键发送。\n如果想只发送给指定用户，请在左侧用户列表中选中该用户，再输入文字并发送，即可发送悄悄话。')
    sc.send(MessageType.server_notification, '您的所有消息都已被加密，能有效防止窃听（但请谨防中间人攻击）。')

    sc.send(MessageType.chat_history_bundle, server.memory.chat_history)

    broadcast(MessageType.on_user_online,
              {"nickname": socket_mappings['nickname'][sc.socket], 'id': socket_mappings['user_id'][sc.socket]})
