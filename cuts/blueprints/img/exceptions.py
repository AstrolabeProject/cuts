#
# Implement exceptions used throughout the app.
#
#   Written by: Tom Hicks. 11/2/2019.
#   Last Modified: Combine with Image MetaData ToolKit errors.
#
class ProcessingError (Exception):
    """
    Base class for exceptions in this module. Overridden by more specific exceptions.

    attributes:
        message -- explanation of the error.
        error_code -- optional integer identifying the exception type: all exception
                      types defined here have a default status/error code.
    """
    ERROR_CODE = 500

    def __init__(self, message, error_code=None):
        Exception.__init__(self)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        else:
            self.error_code = self.ERROR_CODE


    def __str__(self):
        return("({}) {}".format(self.error_code, self.message))


    def to_dict(self):
        retdict = dict()
        retdict['error_code'] = self.error_code
        retdict['message'] = self.message
        return retdict


    def to_tuple(self):
        return (self.message, self.error_code)


class ImageNotFound (ProcessingError):
    """
    Class for exceptions due to specification of missing or unreadable image paths.
    """
    ERROR_CODE = 404

    def __init__(self, message, error_code=ERROR_CODE):
        super().__init__(message, error_code)


class RequestException (ProcessingError):
    """
    Class for exceptions due to requests with missing or invalid arguments.
    """
    ERROR_CODE = 400

    def __init__(self, message, error_code=ERROR_CODE):
        super().__init__(message, error_code)


class ServerError (ProcessingError):
    """
    Class for exceptions caused by unrecoverable internal server errors.
    """
    ERROR_CODE = 500

    def __init__(self, message, error_code=ERROR_CODE):
        super().__init__(message, error_code)


class UnsupportedType (ProcessingError):
    """
    Class for exceptions caused by unsupported file or media types.
    """
    ERROR_CODE = 415

    def __init__(self, message, error_code=ERROR_CODE):
        super().__init__(message, error_code)
