
class StarlitException(Exception):
    """The base exception class for Starlit."""    
    def __init__(self, help_message=None):
        self.help_message = help_message


class FeatureIsDisabled(StarlitException):
    """Raised when trying to initialize a disabled feature"""
