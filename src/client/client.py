from socket import socket, AF_INET, SOCK_STREAM
from src.utils.app_variables import applicationVariables as appVar

"""
This class contains basic logics of a client's communication with the server.
"""


class Client:

    def __init__(self, host, port):
        """
        Establish a connection to the main chat game server.
        :param host: Host of the server
        :param port: Port of the server
        """
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        self.socket_instance.connect((host, port))

    def client_read(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        """
        message = self.socket_instance.recv(appVar.BUFFER_SIZE.value).decode("utf8")
        return message

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send
        """
        self.socket_instance.send(message.encode())

    def close_connection(self):
        """
        Close the connection to the main chat game server.
        """
        self.socket_instance.close()
