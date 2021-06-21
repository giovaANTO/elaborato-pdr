from enum import Enum


class applicationVariables(Enum):
    """
    Client's variables
    """
    # The quit command which close the client's communication with the serve.
    HOST = ""
    PORT = 53000

    QUIT_MESSAGE = "!quit"
    BUFFER_SIZE = 4096
