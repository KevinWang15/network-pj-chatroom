import socket
from pprint import pprint
from common.message import MessageType
from server.memory import socket_mappings, connections


def broadcast(message_type, parameters):
    for connection in connections:
        socket_mappings['sc'][connection].send(message_type, parameters)
