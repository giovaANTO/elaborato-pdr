import time
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
        # Await a welcome message from the server
        message = self.socket_instance.recv(Client.buffer_size).decode("utf8")
        print(message)
        Thread(target=self.__client_loop).start()

    def __client_loop(self):
        """
        Execute the main loop of the Client.
        This method will try to receive messages from the Server object.
        """
        while True:
            try:
                message = self.socket_instance.recv(Client.buffer_size).decode("utf8")
                print(f"[New Message]: {message}")
            except OSError:
                print("Something went wrong")
                break

    def send_message(self, message):
        """
        Send a message to the GameChat server.
        :param message: Message to send
        """
        self.socket_instance.send(message.encode())

window_main = tk.Tk()
window_main.title("Game Client")

myClient = Client('', 53000)
entry_frame = tk.Frame(window_main)
ent_text = tk.Entry(entry_frame)
ent_text.pack(side=tk.LEFT)
btn_send = tk.Button(entry_frame, text="Send", command=lambda: myClient.send_message(ent_text.get()))
btn_send.pack(side=tk.LEFT)
entry_frame.pack(side=tk.BOTTOM)

chat_Frame = tk.Frame(window_main)
scrollBar = tk.Scrollbar(chat_Frame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(chat_Frame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
chat_Frame.pack(side=tk.TOP, pady=(5, 10))

window_main.mainloop()


if __name__ == "__main__":
    client = Client("", 53000)

