from socket import socket, AF_INET, SOCK_STREAM
from src.utils.app_variables import ApplicationVariables as appVar

"""
This class contains basic logics of a client's communication with the server.
"""


class Client:

    def __init__(self, host, port):
        """
        Establish a connection to the main chat game server.
        The client starts in a running status to allow the name sending.
        :param host: Host of the server.
        :param port: Port of the server.
        """
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        self.socket_instance.connect((host, port))
        self.client_status = appVar.CLIENT_RUNNING_STATUS.value

    def client_read(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        :return: message: The checked message read, changed if the message contains a command variable
                to change the client's status.
        """
        message = self.socket_instance.recv(appVar.BUFFER_SIZE.value).decode("utf8")
        return self.check_input_message(message)

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send.
        :return: message: The checked message, empty if the client is stopped.
        """
        return self.check_output_message(message)

    def close_connection(self):
        """
        Close the connection to the main chat game server.
        """
        self.socket_instance.close()

    def check_input_message(self, message):
        """
        Check if the message received by the server is a command to change the Client's status.
        :param message: The input message to check.
        :return: message: The checked message read, changed if the message contains a command variable
                to change the client's status.
        """
        if message == appVar.CLIENT_PAUSED_MESSAGE.value:
            self.client_status = appVar.CLIENT_PAUSED_STATUS.value
            return "You've been paused by the server!\r\n"
        elif message == appVar.CLIENT_RUNNING_MESSAGE.value:
            self.client_status = appVar.CLIENT_RUNNING_STATUS.value
            return "You've been restarted by the server!\r\n"
        else:
            return message

    def check_output_message(self, message):
        """
        Check if the message to send can be sent or not.
        :param message: The message to check before sending.
        :return: The checked message to send, empty if the client's status is paused.
        """
        if (self.client_status == appVar.CLIENT_RUNNING_STATUS.value) or (message == appVar.QUIT_MESSAGE.value):
            self.socket_instance.send(message.encode())
            return message
        elif self.client_status == appVar.CLIENT_PAUSED_STATUS.value:
            return ""
