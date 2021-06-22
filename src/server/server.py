import random
import time
import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from src.utils import roles, questions
from src.utils.app_variables import ApplicationVariables as appVar


class Server:
    buffer_size = 4096
    clients = {}
    scoreboard = {}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.status = appVar.SERVER_STOPPED_STATUS.value

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
        self.status = appVar.SERVER_RUNNING_STATUS.value

    def shutdown_server(self):
        if self.status == appVar.SERVER_RUNNING_STATUS.value:
            for k in self.clients:
                cli = self.clients[k]
                cli.send(appVar.QUIT_MESSAGE.value)
            self.socket_instance.close()
            self.status = appVar.SERVER_STOPPED_STATUS.value


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
            client.send("Welcome to GameChat server!\r\n".encode())
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
        while True:
            # Receive the message of the user containing the name of the player
            name = client_socket.recv(Server.buffer_size).decode("utf8")
            # Check if the name is already present
            if name in self.clients or name in self.scoreboard:
                client_socket.send("Name already used, retry".encode())
            else:
                break

            # Adding the name to the list on new clients
        self.clients[name] = client_socket
        # Adding the name to the scoreboard
        self.scoreboard[name] = {"points": 0, "role": roles.random_role()}
        # Select a role to assign to the new connected client
        # and send it to the new client.
        refresh_scoreboard_list(self.scoreboard)
        
        while True:
            exit_loop = False
            while True:
                try:
                    choice_message = "Make your choice, select a number between 1 and 3\r\n"
                    tricky_choice = random.randint(1, 3)
                    print(f"tricky choice is number {tricky_choice}")
                    client_socket.send(choice_message.encode())
                    choice = client_socket.recv(Server.buffer_size).decode("utf8")
                    if choice == str(tricky_choice) or choice == appVar.QUIT_MESSAGE.value:
                        msg = "You choose the tricky choice, bye...\r\n"
                        client_socket.send(msg.encode())
                        time.sleep(1)
                        msg = appVar.QUIT_MESSAGE.value
                        # Send a disconnection message to the user
                        client_socket.send(msg.encode())
                        # Disconnect the client, closing the opened socket.
                        self.disconnect_client(name)
                        exit_loop = True
                        break
                    elif int(choice) > 3:
                        print("Error while selecting option")
                    else:
                        break
                except Exception:
                    print("Error while selecting option")

            if exit_loop:
                break

            question, correct_answer = questions.select_question()[1]
            client_socket.send(question.encode())
            answer_given = client_socket.recv(Server.buffer_size).decode("utf8")
            info = self.scoreboard[name]

            if correct_answer == answer_given:
                info.update({"points": info.get("points") + 1})
                msg = "Correct answer!"
            elif answer_given == appVar.QUIT_MESSAGE.value:
                msg = appVar.QUIT_MESSAGE.value
                client_socket.send(msg.encode())
                self.disconnect_client(name)
            else:
                info.update({"points": info.get("points") - 1})
                msg = "Wrong answer!"

            refresh_scoreboard_list(self.scoreboard)
            client_socket.send(msg.encode())

    def disconnect_client(self, name):
        """
        Close a connection to a client, deleting all the references
        :param name: the name of the client to delete
        """
        self.clients[name].close()
        del self.clients[name]
        del self.scoreboard[name]
        refresh_scoreboard_list(self.scoreboard)


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


def refresh_scoreboard_list(scoreboard):
    textList.config(state=tk.NORMAL)
    textList.delete('1.0', tk.END)

    for name in scoreboard:
        points = scoreboard[name].get("points")
        role = scoreboard[name].get("role")
        textList.insert(tk.END, f"{name} - {points} - {role} \n")

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
