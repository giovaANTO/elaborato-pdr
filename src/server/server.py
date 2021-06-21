import random
import tkinter as tk

from src.server.server_status import ServerStatus
from src.utils import roles
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class Server:
    buffer_size = 4096
    clients = {}
    addresses = []
    scoreboard = {}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.status = ServerStatus.STOP

    def start_server(self):
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        # Create a new TCP connection socket for the Server communication
        print(f"Setup server connection on host:{self.host} and port:{self.port}")
        # Bind the server socket to an host (default value host) and a port
        self.socket_instance.bind((self.host, self.port))
        self.socket_instance.listen(10)
        print(f"Starting up a new server thread")
        # Create a new thread instance that use the accpet_connection function as handler
        thread = Thread(target=self.__accept_connection)
        # Start the thread
        thread.start()
        self.status = ServerStatus.RUN

    def shutdown_server(self):
        if self.status == ServerStatus.RUN:
            self.socket_instance.close()
            self.status = ServerStatus.STOP

    def __accept_connection(self):
        """
        This method is used for tracking new clients that are connected to the server for
        participating in a new game.
        """
        print("Awaiting new connections...")
        while True:
            # Wait for new clients to connect
            client, address = self.socket_instance.accept()
            print(f"New client connected : {address}")
            self.addresses.append(address)
            refresh_addresses(self.addresses)
            client.send("You've successfully connected to GameChat server!\r\n".encode())
            client.send("To start playing please type your name\r\n".encode())
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
        print(name)
        # Adding the name to the list on new clients
        self.clients[name] = client_socket
        # Adding the name to the scoreboard
        self.scoreboard[name] = {"points": 0, "role": roles.random_role()}
        # Select a role to assign to the new connected client
        # and send it to the new client.
        while True:
            choice_message = "Make your choice, select a number between 1 and 3\r\n"
            tricky_choice = random.randint(1, 3)
            print(f"tricky choice is number {tricky_choice}")
            client_socket.send(choice_message.encode())
            choice = client_socket.recv(Server.buffer_size).decode("utf8")

            if choice == tricky_choice or choice == "quit":
                msg = "You've chosen a tricky option, you'll be disconnected" if choice == tricky_choice else "Quitting\r\n"
                # Send a disconnection message to the user
                client_socket.send(msg.encode())
                # Disconnect the client, closing the opened socket.
                self.disconnect_client(name)
                break

    def disconnect_client(self, name):
        """
        Close a connection to a client, deleting all the references
        :param name: the name of the client to delete
        """
        self.clients[name].close()
        del self.clients[name]
        del self.scoreboard[name]
        self.broadcast_message(f"{name} left the game")

    def broadcast_message(self, message):
        """
        Broadcast a message to all the connected clients
        :param message:
            The message to send
        """
        for client in self.clients.values():
            client.send(message.encode())

    def get_port(self):
        return self.port

    def get_host(self):
        return self.host


def __startup_server_cmd():
    server.start_server()
    startServerButton.config(state=tk.DISABLED)
    shutdownServerButton.config(state=tk.NORMAL)


def __shutdown_server_cmd():
    server.shutdown_server()
    startServerButton.config(state=tk.NORMAL)
    shutdownServerButton.config(state=tk.DISABLED)


def __close_window_cmd():
    server.shutdown_server()
    root.quit()


def refresh_addresses(addresses):
    textList.config(state=tk.NORMAL)
    textList.delete('1.0', tk.END)

    for a in addresses:
        textList.insert(tk.END, f"{a}\n")

    textList.config(state=tk.DISABLED)


if __name__ == "__main__":
    server = Server('', 53000)

    root = tk.Tk()
    root.geometry("300x200")
    root.title("GameChat server")

    startupFrame = tk.Frame(root)
    startServerButton = tk.Button(startupFrame, text="Start", command=lambda: __startup_server_cmd())
    shutdownServerButton = tk.Button(startupFrame, text="Shutdown", command=lambda: __shutdown_server_cmd(),
                                     state=tk.DISABLED)

    startServerButton.pack(side=tk.LEFT)
    shutdownServerButton.pack(side=tk.RIGHT)
    startupFrame.pack(side=tk.TOP, pady=(10, 0))

    clientListFrame = tk.Frame(root)
    clientListFrameTitle = tk.Label(clientListFrame, text="Connected clients:").pack()
    textList = tk.Text(clientListFrame, height=10, width=30)
    textList.tag_configure("center", justify="center")
    textList.config(state=tk.DISABLED)
    textList.pack()
    clientListFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    root.protocol("WM_DELETE_WINDOW", __close_window_cmd)
    root.mainloop()
