import tkinter as tk
from src.server.server import Server


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
