from enum import Enum


class applicationVariables(Enum):
    """
    Client's variables
    """
    # The quit command which close the client's communication with the serve.
    QUIT_MESSAGE = "!quit"

    HOST = ""
    PORT = 53000

    BUFFER_SIZE = 4096
