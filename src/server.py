from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class Server:
    buffer_size = 4096
    clients = {}

    def __init__(self, host, port):
        # Create a new TCP connection socket for the Server communication
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        print(f"Setup server connection on host:{host} and port:{port}")
        # Bind the server socket to an host (default value host) and a port
        self.socket_instance.bind((host, port))
        self.socket_instance.listen(10)
        print(f"Starting up a new server thread")
        # Create a new thread instance that use the accpet_connection function as handler
        thread = Thread(target=self.__accept_connection)
        # Start the thread
        thread.start()
        # Waiting for a result from the running thread.
        thread.join()
        # When the thread has returned close the current connection
        self.socket_instance.close()

    def __accept_connection(self):
        """
        This method is used for the tracking of new clients that will connect to the server for
        participating in a new game.
        """
        print("Awaiting new connections...")
        while True:
            # Wait for new clients to connect
            client, address = self.socket_instance.accept()
            print(f"New client connected : {address}")
            # Sending a welcoming message to the newly connected client
            client.send("Hello, Welcome in the ChatGame server".encode())
            # The connected client should type its name for continue
            client.send("Please, type your name for continue:".encode())
            # Setting up a new thread for the newly created client.
            # The thread will use the __manage_client function
            client_thread = Thread(target=self.__manage_client, args=(client,))
            # Starting up the thread.
            client_thread.start()

    def __manage_client(self, client_socket):
        """
        This method is used for managing the connected clients. 
        :param client_socket: The socket used for the communication with the client
        """
        # Receive the message of the user containing the name of the player
        name = client_socket.recv(Server.buffer_size).decode("utf8")
        welcome_message = f"Welcome on the game server {name} !\n"
        broadcast_message = f"User : {name} joined in the Chat Game server\n"

        # Adding the record to the list on new clients
        self.clients[client_socket] = name
        # Sending the welcoming message
        client_socket.send(welcome_message.encode())
        # Broadcast to the other clients that the user has joined the server
        self.broadcast_message(broadcast_message)

        while True:
            # Await to receive a message from the user
            msg = client_socket.recv(Server.buffer_size).decode("utf8")
            if msg == "quit":
                # Disconnect the client, closing the opened socket.
                del self.clients[client_socket]
                client_socket.send("quit".encode())
                client_socket.close()
                self.broadcast_message(f"{name} left the chat\n")
                break

    def broadcast_message(self, message):
        """
        Broadcast a message to all the connected clients
        :param message:
            The message to send
        """
        for client in self.clients:
            client.send(message.encode())


if __name__ == "__main__":
    Server('', 53000)
