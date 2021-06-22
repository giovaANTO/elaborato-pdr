from enum import Enum


class ApplicationVariables(Enum):
    """
    Client variables
    """
    CLIENT_RUNNING_STATUS = 1
    CLIENT_PAUSED_STATUS = 2

    """
    Server variables
    """
    SERVER_RUNNING_STATUS = 1
    SERVER_STOPPED_STATUS = 2

    """
    Shared variables
    """
    HOST = ""
    PORT = 53000
    BUFFER_SIZE = 4096

    """
    Command variables
    """
    # The quit command which close the client's communication with the serve.
    QUIT_MESSAGE = "!quit"
    CLIENT_PAUSED_MESSAGE = "!pause"
    CLIENT_RUNNING_MESSAGE = "!run"