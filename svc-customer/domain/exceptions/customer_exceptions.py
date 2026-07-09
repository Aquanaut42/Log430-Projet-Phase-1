# customer_exceptions.py

class CustomerAlreadyExists(Exception):
    pass

class CustomerNotFound(Exception):
    pass

class InvalidOTP(Exception):
    pass

class CustomerNotActive(Exception):
    pass
