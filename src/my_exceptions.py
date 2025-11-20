class CustomException(Exception):
    def __init__(self, name, status, message):
        self.name = name
        self.status = status
        self.message = message
