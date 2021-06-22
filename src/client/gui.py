import tkinter as tk
from threading import Thread
from src.utils.app_variables import applicationVariables as appVar
from src.client.client import Client


def receive():
    """
    This method is used as loop to listen to messages that socket receives.
    """
    while True:
        try:
            # Receive method uses the client class to listen to socket's messages.
            message = my_client.client_read()
            # If message contains the quit command, client's communication must be closed.
            # Else the message's list is shown on screen.
            if message == appVar.QUIT_MESSAGE.value:
                on_closing()
            message_list.insert(tk.END, message)
            # In case an error occurs, probably the client left the chat.
        except OSError:
            break


def send(event=None):
    """
    This method is used to send a message to the server.
    """
    # If the user has written a message, it's sent to the server.
    if len(my_message.get()) > 0:
        message = my_message.get()
        # The message is shown on screen.
        message_list.insert(tk.END, message)
        # The input box is erased.
        my_message.set("")
        # The message is then sent to the server.
        my_client.send_message(message)
        # If the message contains the quit command, communications must be interrupted.
        if message == appVar.QUIT_MESSAGE.value:
            my_client.close_connection()
            root.quit()


def on_closing(event=None):
    """
    This method is used to close the client's communication with the server.
    """
    # Communication is closed by forcing the message to quit command.
    my_message.set(appVar.QUIT_MESSAGE.value)
    send()


# *********** GUI PART ***************
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Client_GUI")

    messages_frame = tk.Frame(root)
    # A StringVar variable to manage messages to sent.
    my_message = tk.StringVar()
    # A scrollbar to show all the messages contained in the ListBox.
    scrollbar = tk.Scrollbar(messages_frame)

    # A Listbox to contain all the messages, and a scrollbar attached to see all of them.
    message_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    message_list.pack(side=tk.LEFT, fill=tk.BOTH)
    message_list.pack()
    messages_frame.pack()

    # The Entry field where user types the messages.
    entry_field = tk.Entry(root, textvariable=my_message)
    # Link the send method to the Return command.
    entry_field.bind("<Return>", send)

    entry_field.pack()
    # Link the send method to the send button.
    send_button = tk.Button(root, text="Send", command=send)
    send_button.pack()

    # Handel the closing window event.
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # *********** CONNECTION PART ***************

    # Set a new client's communication with the server.
    my_client = Client(appVar.HOST.value, appVar.PORT.value)
    # Starting client's loop as the receive method.
    Thread(target=receive).start()

    # Start gui.
    tk.mainloop()
