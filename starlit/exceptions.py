
class StarlitException(Exception):
    """The base exception class for Starlit."""    
    def __init__(self, help_message=None):
        self.help_message = help_message


class StarlitConfigurationError(StarlitException):
    """Raised when trying to initialize a disabled feature"""


class BadlyFormattedFixture(StarlitException):
    """Raised when a json.JSONDecodeError exception is raised."""