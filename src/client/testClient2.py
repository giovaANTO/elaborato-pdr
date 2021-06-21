from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk

from src.client.testClient import Client

quit_message = "!quit"

def receive():
    while True:
        try:
            #quando viene chiamata la funzione receive, si mette in ascolto dei messaggi che
            #arrivano sul socket
            message = my_client.client_read()
            #visualizziamo l'elenco dei messaggi sullo schermo
            #e facciamo in modo che il cursore sia visibile al termine degli stessi
            if message == quit_message:
                on_closing()
            message_list.insert(tk.END, message)
            # Nel caso di errore e' probabile che il client abbia abbandonato la chat.
        except OSError:
            break

def send(event=None):
    # gli eventi vengono passati dai binders.
    if(len(my_message.get()) > 0):
        message = my_message.get()
        # libera la casella di input.
        my_message.set("")
        # invia il messaggio sul socket
        my_client.send_message(message)
        if message == quit_message:
            my_client.close_connection()
            root.quit()

def on_closing(event=None):
    my_message.set(quit_message)
    send()

root = tk.Tk()
root.title("Client_GUI")

#creiamo il Frame per contenere i messaggi
messages_frame = tk.Frame(root)
#creiamo una variabile di tipo stringa per i messaggi da inviare.
my_message = tk.StringVar()
#indichiamo all'utente dove deve scrivere i suoi messaggi
my_message.set("Scrivi qui i tuoi messaggi.")
#creiamo una scrollbar per navigare tra i messaggi precedenti.
scrollbar = tk.Scrollbar(messages_frame)

# La parte seguente contiene i messaggi.
message_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
message_list.pack(side=tk.LEFT, fill=tk.BOTH)
message_list.pack()
messages_frame.pack()

#Creiamo il campo di input e lo associamo alla variabile stringa
entry_field = tk.Entry(root, textvariable=my_message)
# leghiamo la funzione send al tasto Return
entry_field.bind("<Return>", send)

entry_field.pack()
#creiamo il tasto invio e lo associamo alla funzione send
send_button = tk.Button(root, text="Invio", command=send)
#integriamo il tasto nel pacchetto
send_button.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

#----Connessione al Server----

host = ""
port = 53000
buffer_size = 1024

my_client = Client(host, port)
Thread(target=receive).start()

# Avvia l'esecuzione della Finestra Chat.

tk.mainloop()