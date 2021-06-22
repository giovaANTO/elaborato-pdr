from socket import socket, AF_INET, SOCK_STREAM
from src.utils.app_variables import ApplicationVariables as appVar

"""
This class contains basic logics of a client's communication with the server.
"""


class Client:

    client_status = 0

    def __init__(self, host, port):
        """
        Establish a connection to the main chat game server.
        :param host: Host of the server
        :param port: Port of the server
        """
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        self.socket_instance.connect((host, port))
        self.client_status = appVar.CLIENT_RUNNING_STATUS.value

    def client_read(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        """
        message = self.socket_instance.recv(appVar.BUFFER_SIZE.value).decode("utf8")
        self.check_message(message)
        return message

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send
        """
        if self.client_status == appVar.CLIENT_RUNNING_STATUS.value:
            self.socket_instance.send(message.encode())

    def close_connection(self):
        """
        Close the connection to the main chat game server.
        """
        self.socket_instance.close()

    def check_message(self, message):
        if message == appVar.CLIENT_PAUSED_MESSAGE.value:
            self.client_status = appVar.CLIENT_PAUSED_STATUS.value
        if message == appVar.CLIENT_RUNNING_MESSAGE.value:
            self.client_status = appVar.CLIENT_RUNNING_STATUS.value
