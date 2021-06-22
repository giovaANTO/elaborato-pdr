import random
import sys
import time
import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from src.utils import roles, questions
from src.utils.app_variables import ApplicationVariables as appVar


class Server:
    clients = {}
    scoreboard = {}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_status = appVar.SERVER_STOPPED_STATUS.value
        self.match_status = appVar.SERVER_MATCH_PAUSED.value

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
        self.server_status = appVar.SERVER_RUNNING_STATUS.value

    def shutdown_server(self):
        if self.server_status == appVar.SERVER_RUNNING_STATUS.value:
            print("Shutdown server....closing all client instances")
            clients = self.clients.copy()
            for name in clients:
                self.disconnect_client(name)
            try:
                self.socket_instance.close()
                self.server_status = appVar.SERVER_STOPPED_STATUS.value
                self.match_status = appVar.SERVER_MATCH_PAUSED.value
            except Exception as e:
                print(f"Error : {str(e)}")

    def __accept_connection(self):
        """
        This method is used for tracking new clients that are connected to the server for
        participating in a new game.
        """
        print("Awaiting new connections...")
        while True:
            # Wait for new clients to connect
            try :
                client, address = self.socket_instance.accept()
            except ConnectionAbortedError:
                sys.exit(0)

            print(f"New client connected : {address}")
            client.send("Welcome to GameChat server!\r\n".encode())
            client.send("To start playing please type your name\r\n".encode())
            # Setting up a new thread for the newly created client.
            # The thread will use the __manage_client function
            client_thread = Thread(target=self.__manage_client, args=(client,))
            # Starting up the thread.
            client_thread.start()

    def __timer_handler(self):
        self.broadcast_message("Ready in 5 seconds")
        self.match_status = appVar.SERVER_MATCH_STARTED.value
        time.sleep(5)
        self.broadcast_message(appVar.CLIENT_RUNNING_MESSAGE.value)
        match_timer = appVar.MATCH_TIMER.value
        while match_timer >= 0:
            if self.server_status == appVar.SERVER_STOPPED_STATUS.value:
                sys.exit(0)
            else:
                print(match_timer)
                time.sleep(1)
                match_timer -= 1
        self.match_status = appVar.SERVER_MATCH_PAUSED.value
        if len(self.scoreboard) > 0:
            self.broadcast_message(appVar.CLIENT_PAUSED_MESSAGE.value)
            time.sleep(1)
            winner, points = self.__get_max_player()
            print(winner, points)
            self.broadcast_message(f"the winner is {winner} with {points} points")
            time.sleep(4)
            shutdown_server_cmd()

    def __get_max_player(self):
        max_score = []
        for name in self.scoreboard:
            points = self.scoreboard[name]["points"]
            if (max_score and points >= max_score[1]) or len(max_score) == 0:
                max_score = [name, points]
        return max_score

    def __manage_client(self, client_socket):
        """
        This method is used for managing the connected clients.
        :param client_socket: The socket used for the communication with the client
        """
        while True:
            # Receive the message of the user containing the name of the player
            name = self.receive_message(client_socket)
            # Check if the name is already present
            if name in self.clients or name in self.scoreboard:
                self.send_message("Name already used, retry", client_socket)
            elif name == appVar.QUIT_MESSAGE.value:
                sys.exit(0)
            else:
                break

        self.register_client(name, client_socket)
        while self.match_status != appVar.SERVER_MATCH_STARTED.value:
            time.sleep(2)

        while True:
            while True:
                try:
                    choice_message = "Make your choice, select a number between 1 and 3\r\n"
                    tricky_choice = random.randint(1, 3)
                    print(f"tricky choice is number {tricky_choice}")
                    self.send_message(choice_message, client_socket)
                    choice = self.receive_message(client_socket)
                    if choice == str(tricky_choice):
                        msg = "You choose the tricky choice, bye...\r\n"
                        self.send_message(msg, client_socket)
                        time.sleep(1)
                        self.disconnect_client(name)
                        sys.exit(0)
                    elif choice == appVar.QUIT_MESSAGE.value:
                        self.disconnect_client(name)
                        sys.exit(0)
                    elif int(choice) > 3:
                        print(f"[Inside loop] Error while selecting option")
                    else:
                        break
                except OSError as ose:
                    sys.exit(0)
                except Exception as e:
                    print(f"[Exception] unexpected error {str(e)}")

            question, correct_answer = questions.select_question()[1]
            self.send_message(question, client_socket)
            answer_given = self.receive_message(client_socket)
            info = self.scoreboard[name]

            if correct_answer == answer_given:
                info.update({"points": info.get("points") + 1})
                msg = "Correct answer!"
            elif answer_given == appVar.QUIT_MESSAGE.value:
                msg = appVar.QUIT_MESSAGE.value
                self.send_message(msg, client_socket)
                self.disconnect_client(name)
                sys.exit(0)
            else:
                info.update({"points": info.get("points") - 1})
                msg = "Wrong answer!"

            refresh_scoreboard_list(self.scoreboard)
            self.send_message(msg, client_socket)

    def register_client(self, name, client_socket):
        if len(self.clients) < appVar.MIN_PARTICIPANTS.value and self.match_status == appVar.SERVER_MATCH_PAUSED.value:
            self.send_message(appVar.CLIENT_PAUSED_MESSAGE.value, client_socket)
            # Adding the name to the list on new clients
            self.clients[name] = {"socket": client_socket, "status": appVar.CLIENT_PAUSED_STATUS.value}
            # Adding the name to the scoreboard
            self.scoreboard[name] = {"points": 0, "role": roles.random_role()}
            # Select a role to assign to the new connected client
            # and send it to the new client.
            refresh_scoreboard_list(self.scoreboard)
            if len(self.clients) == appVar.MIN_PARTICIPANTS.value:
                print("Timer started")
                Thread(target=self.__timer_handler).start()
            else:
                remaining = appVar.MIN_PARTICIPANTS.value - len(self.clients)
                self.broadcast_message(f"waiting for :  {remaining} more participants")
        else:
            self.send_message("A game is just started, please retry later", client_socket)
            time.sleep(1)
            self.send_message(appVar.QUIT_MESSAGE.value, client_socket)

    def disconnect_client(self, name):
        """
        Close a connection to a client, deleting all the references
        :param name: the name of the client to delete
        """
        client = self.clients[name]["socket"]
        msg = appVar.QUIT_MESSAGE.value
        # Send a disconnection message to the user
        self.send_message(msg,client)
        # Disconnect the client, closing the opened socket.
        client.close()
        del self.clients[name]
        del self.scoreboard[name]
        refresh_scoreboard_list(self.scoreboard)

    def send_message(self, message, client):
        client.send(message.encode())

    def receive_message(self, client_socket):
        try:
            msg = client_socket.recv(appVar.BUFFER_SIZE.value).decode("utf8")
            return msg
        except ConnectionAbortedError:
            sys.exit(1)

    def broadcast_message(self, message):
        for name in self.clients:
            client = self.clients[name]["socket"]
            self.send_message(message, client)


def startup_server_cmd():
    server.start_server()
    startServerButton.config(state=tk.DISABLED)
    shutdownServerButton.config(state=tk.NORMAL)


def shutdown_server_cmd():
    server.shutdown_server()
    startServerButton.config(state=tk.NORMAL)
    shutdownServerButton.config(state=tk.DISABLED)


def close_window_cmd():
    root.quit()
    server.shutdown_server()



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
    startServerButton = tk.Button(startupFrame, text="Start", command=lambda: startup_server_cmd())
    shutdownServerButton = tk.Button(startupFrame, text="Shutdown", command=lambda: shutdown_server_cmd(),
                                     state=tk.DISABLED)

    startServerButton.pack(side=tk.LEFT)
    shutdownServerButton.pack(side=tk.RIGHT)
    startupFrame.pack(side=tk.TOP, pady=(10, 0))

    clientListFrame = tk.Frame(root)
    clientListFrameTitle = tk.Label(clientListFrame, text="Scoreboard:").pack()
    textList = tk.Text(clientListFrame, height=10, width=30)
    textList.tag_configure("center", justify="center")
    textList.config(state=tk.DISABLED)
    textList.pack()
    clientListFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    root.protocol("WM_DELETE_WINDOW", close_window_cmd)
    root.mainloop()
