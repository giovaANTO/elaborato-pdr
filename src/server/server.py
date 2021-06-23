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
        """
        Starts the server establishing a new tcp socket connection and creat
        new thread that will handle the new clients connections
        """
        # Establish a new socket connection
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
        # Setting the server on running status
        self.server_status = appVar.SERVER_RUNNING_STATUS.value

    def shutdown_server(self):
        """
        Shutdown the server, disconnecting the current client
        sockets.
        """
        # Check if the server is a running status
        if self.server_status == appVar.SERVER_RUNNING_STATUS.value:
            print("Shutdown server....closing all client instances")
            clients = self.clients.copy()
            for name in clients:
                # Disconnect each clients
                self.disconnect_client(name)
            try:
                # Closing the server socket instance
                self.socket_instance.close()
                # Setting the server in a stopped status
                self.server_status = appVar.SERVER_STOPPED_STATUS.value
                # Setting the match status to paused
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
            try:
                # Accept a new connection from a client
                client, address = self.socket_instance.accept()
            except ConnectionAbortedError:
                sys.exit(0)

            print(f"New client connected : {address}")
            # Sending a welcome message to newly created client
            self.send_message("Welcome to GameChat server! type your name to begin\r\n",client)
            # Setting up a new thread for the newly created client.
            # The thread will use the __manage_client function
            client_thread = Thread(target=self.__manage_client, args=(client,))
            # Starting up the thread.
            client_thread.start()

    def __timer_handler(self):
        """
        Game time handler function.
        This is used in a thread to handle the passing time in the game.
        """
        # Broadcast to clients that the game will begin in 5 seconds
        self.broadcast_message("Ready in 5 seconds")
        # Sets the match status flag to start
        self.match_status = appVar.SERVER_MATCH_STARTED.value
        time.sleep(5)
        # Unlock the clients
        self.broadcast_message(appVar.CLIENT_RUNNING_MESSAGE.value)
        # Starts the countdown
        match_timer = appVar.MATCH_TIMER.value
        while match_timer >= 0:
            # If the server is stopped exit from the thread
            if self.server_status == appVar.SERVER_STOPPED_STATUS.value:
                sys.exit(0)
            # If there aren't any clients left exit from the loop
            elif len(self.clients) == 0:
                break
            else:
                time.sleep(1)
                match_timer -= 1
        # Countdown terminated
        # Pause the game
        self.match_status = appVar.SERVER_MATCH_PAUSED.value
        if len(self.scoreboard) > 0:
            # If there are any clients lock them
            self.broadcast_message(appVar.CLIENT_PAUSED_MESSAGE.value)
            time.sleep(1)
            # Print the winning participant name and relative points
            winner, points = self.__get_max_player()
            self.broadcast_message(f"the winner is {winner} with {points} points")
            time.sleep(4)

        # Shutdown the server
        shutdown_server_cmd()

    def __get_max_player(self):
        """
        Get the player with the higher score in the game
        :return: A list with the name of a player and the relative score
        """
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
            # Exit from the application if the message is equal to the quit command
            elif name == appVar.QUIT_MESSAGE.value:
                sys.exit(0)
            else:
                break
        # Register a new client in the game
        self.register_client(name, client_socket)
        # Wait for other clients to join the server
        while self.match_status != appVar.SERVER_MATCH_STARTED.value:
            time.sleep(2)

        # Main loop
        while True:

            '''
            This first loop will allow the player to select 3 options
            one of these is choosed randomly and if selected will kick the client out from the server.
            The other two option will select one question randomly from a list and if the player will answer correctly
            to this then its score will increment to one point or decrement to one point otherwise.
            '''
            while True:
                try:
                    choice_message = "Make your choice, select a number between 1 and 3\r\n"
                    # Choose randomly the option that will kick out the client from the server
                    tricky_choice = random.randint(1, 3)
                    self.send_message(choice_message, client_socket)
                    choice = self.receive_message(client_socket)
                    # Tricky choice selected
                    if choice == str(tricky_choice):
                        msg = "You choose the tricky choice, bye...\r\n"
                        self.send_message(msg, client_socket)
                        time.sleep(1)
                        # Disconnect the client
                        self.disconnect_client(name)
                        # Quit the thread
                        sys.exit(0)
                    # !quit command sent
                    elif choice == appVar.QUIT_MESSAGE.value:
                        # Disconnect the client from the server
                        self.disconnect_client(name)
                        # Quit the thread
                        sys.exit(0)
                    # Invalid choice
                    elif int(choice) > 3 or int(choice) < 1:
                        print(f"[Inside loop] Error while selecting option")
                    else:
                        break
                except OSError as ose:
                    sys.exit(0)
                except Exception as e:
                    print(f"[Exception] unexpected error {str(e)}")

            # Select a random question with relative answer from the list
            question, correct_answer = questions.select_question()[1]
            self.send_message(question, client_socket)
            # Receive the answer from the client
            answer_given = self.receive_message(client_socket)
            info = self.scoreboard[name]

            # Correct answer given
            if correct_answer == answer_given:
                info.update({"points": info.get("points") + 1})
                msg = "Correct answer!"
            # !quit command sent
            elif answer_given == appVar.QUIT_MESSAGE.value:
                msg = appVar.QUIT_MESSAGE.value
                self.send_message(msg, client_socket)
                self.disconnect_client(name)
                sys.exit(0)
            else:
                info.update({"points": info.get("points") - 1})
                msg = "Wrong answer!"

            # Refresh the scoreboard in the gui
            refresh_scoreboard_list(self.scoreboard)
            self.send_message(msg, client_socket)

    def register_client(self, name, client_socket):
        """
        Register a client in the server
        :param name: the name of the client
        :param client_socket: the communication socket of the client
        """

        # Check if the client can join in the server
        if len(self.clients) < appVar.PARTICIPANTS.value and self.match_status == appVar.SERVER_MATCH_PAUSED.value:
            self.send_message(appVar.CLIENT_PAUSED_MESSAGE.value, client_socket)
            # Adding the name to the list on new clients
            self.clients[name] = {"socket": client_socket, "status": appVar.CLIENT_PAUSED_STATUS.value}
            # Adding the name to the scoreboard
            self.scoreboard[name] = {"points": 0, "role": roles.random_role()}
            # Select a role to assign to the new connected client
            # and send it to the new client.
            refresh_scoreboard_list(self.scoreboard)
            # If the minimum number of participants is reached then start a timer thread that will handle
            # the game flow
            if len(self.clients) == appVar.PARTICIPANTS.value:
                print("Timer started")
                Thread(target=self.__timer_handler).start()
            # Print to clients the remaining number of clients that should joint the server for starting the game
            else:
                remaining = appVar.PARTICIPANTS.value - len(self.clients)
                self.broadcast_message(f"waiting for :  {remaining} more participants")
        # Disallow the client to join the game
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
        self.send_message(msg, client)
        # Disconnect the client, closing the opened socket.
        client.close()
        # Delete the reference from client list
        del self.clients[name]
        # Delete the reference from the scoreboard list
        del self.scoreboard[name]
        # Refresh the scoreboard on the gui
        refresh_scoreboard_list(self.scoreboard)

    def send_message(self, message, client_socket):
        """
        Send a message to a client
        :param message: The message to send
        :param client_socket: The client socket that will receive the message
        """
        client_socket.send(message.encode())

    def receive_message(self, client_socket):
        """
        Listen for an incoming message from a client socket
        :param client_socket: the target client socket
        """
        try:
            msg = client_socket.recv(appVar.BUFFER_SIZE.value).decode("utf8")
            return msg
        except ConnectionAbortedError:
            sys.exit(1)

    def broadcast_message(self, message):
        """
        Broadcast a message to all the clients
        :param message: Message to broadcast
        """
        for name in self.clients:
            client = self.clients[name]["socket"]
            self.send_message(message, client)


def startup_server_cmd():
    """
    Function invoked on the pressing of start button in the gui
    """
    server.start_server()
    startServerButton.config(state=tk.DISABLED)
    shutdownServerButton.config(state=tk.NORMAL)


def shutdown_server_cmd():
    """
    Function invoked on the pressing of shutdown button in the gui
    """
    server.shutdown_server()
    startServerButton.config(state=tk.NORMAL)
    shutdownServerButton.config(state=tk.DISABLED)


def close_window_cmd():
    """
    Function invoked on the system event WM_DELETE_WINDOW
    """
    root.quit()
    server.shutdown_server()


def refresh_scoreboard_list(scoreboard):
    """
    Refresh the scoreboard list in the gui
    :param scoreboard: The scoreboard dictionary
    """
    textList.config(state=tk.NORMAL)
    textList.delete('1.0', tk.END)
    for name in scoreboard:
        points = scoreboard[name].get("points")
        role = scoreboard[name].get("role")
        textList.insert(tk.END, f"{name} - {points} - {role} \n")
    textList.config(state=tk.DISABLED)


# *********** GUI PART ***************

if __name__ == "__main__":
    server = Server(appVar.HOST.value, appVar.PORT.value)

    root = tk.Tk()
    root.geometry("300x200")
    root.title("GameChat server")

    startupFrame = tk.Frame(root)
    # The start button, allows server to listen to new connections.
    startServerButton = tk.Button(startupFrame, text="Start", command=lambda: startup_server_cmd())
    # The shutdown button, closes server's connections and doesn't allow it to listen to new connections
    # until the start button is clicked again.
    shutdownServerButton = tk.Button(startupFrame, text="Shutdown", command=lambda: shutdown_server_cmd(),
                                     state=tk.DISABLED)

    startServerButton.pack(side=tk.LEFT)
    shutdownServerButton.pack(side=tk.RIGHT)
    startupFrame.pack(side=tk.TOP, pady=(10, 0))

    # A Frame to show all the clients actually connected, their score and role.
    clientListFrame = tk.Frame(root)
    clientListFrameTitle = tk.Label(clientListFrame, text="Scoreboard:").pack()
    textList = tk.Text(clientListFrame, height=10, width=30)
    textList.tag_configure("center", justify="center")
    textList.config(state=tk.DISABLED)
    textList.pack()
    clientListFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    # Handle the closing window event.
    root.protocol("WM_DELETE_WINDOW", close_window_cmd)
    # Start the gui.
    root.mainloop()
