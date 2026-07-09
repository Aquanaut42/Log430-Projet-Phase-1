# order_exceptions.py

class OrderAlreadyExists(Exception):
    pass

class OrderNotFound(Exception):
    pass

class LineNotFound(Exception):
    pass

class LineAlreadyExists(Exception):
    pass

class CustomerNotActive(Exception):
    pass

class PlanNotFound(Exception):
    pass
