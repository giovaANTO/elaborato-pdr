import time
import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

class Client:

    buffer_string = ""
    buffer_size = 4096

    def __init__(self, host, port):
        """
        Estabilish a connection to the main chat game server
        :param host: Host of the server
        :param port: Port of the server
        """
        self.socket_instance = socket(AF_INET, SOCK_STREAM)
        self.socket_instance.connect((host, port))
        # Await a welcome message from the server
        message = self.socket_instance.recv(Client.buffer_size).decode("utf8")
        Client.append_string(message)
        Thread(target=self.__client_loop).start()

    def __client_loop(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        """
        new_message = "[New Message]: "
        error_message = "Something went wrong.."
        while True:
            try:
                message = self.socket_instance.recv(Client.buffer_size).decode("utf8")
                Client.append_string(new_message + message)
            except OSError:
                Client.append_string(error_message)
                break

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send
        """
        self.socket_instance.send(message.encode())

    def append_string(self, message_to_append):
        Client.buffer_string += message_to_append

    def get_string(self):
        output = Client.buffer_string
        Client.buffer_string = ""
        return output

if __name__ == "__main__":

    my_client = Client("", 53000)

    root = tk.Tk()
    root.geometry("300x200")
    root.title("Game Client")

    entry_frame = tk.Frame(root)
    ent_text = tk.Entry(entry_frame)
    ent_text.pack(side=tk.LEFT)
    btn_send = tk.Button(entry_frame, text="Send", command=lambda: my_client.send_message(ent_text.get()))
    btn_send.pack(side=tk.LEFT)
    entry_frame.pack(side=tk.BOTTOM)

    chat_Frame = tk.Frame(root)
    scroll_bar = tk.Scrollbar(chat_Frame)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    tk_display = tk.Text(chat_Frame, height=10, width=30)
    tk_display.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
    scroll_bar.config(command=tk_display.yview)
    tk_display.config(yscrollcommand=scroll_bar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
    chat_Frame.pack(side=tk.TOP, pady=(5, 10))

    root.mainloop()
