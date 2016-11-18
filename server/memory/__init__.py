socket_mappings = {
    "user_id": {},
    "nickname": {},
    'sc': {}
}

connections = []

user_id_incr = 1


def remove_from_socket_mapping(socket):
    for key, value in socket_mappings.items():
        if (socket in socket_mappings[key]):
            del socket_mappings[key][socket]


def get_online_users():
    users = []
    for key, value in socket_mappings['user_id'].items():
        user_id = value
        if not key in socket_mappings['nickname']:
            continue
        nickname = socket_mappings['nickname'][key]
        users.append({"nickname": nickname, 'id': user_id})

    return users
