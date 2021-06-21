import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

class Client:

    buffer_size = 4096

    def __init__(self, host, port):
        """
        Estabilish a connection to the main chat game server
        :param host: Host of the server
        :param port: Port of the server
        """
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        self.socket_instance.connect((host, port))
        #Thread(target=self.__client_loop).start() #Da risolvere!!

    def client_read(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        """
        message = self.socket_instance.recv(Client.buffer_size).decode("utf8")
        return message

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send
        """
        self.socket_instance.send(message.encode())

    def close_connection(self):
        self.socket_instance.close()
