activeFunctions = set()

def noRecusion(function):
    """The decorated function should not return any values"""
    def wrapper(*args, **kwargs):
        identifier = id(function)
        if identifier not in activeFunctions:
            activeFunctions.add(identifier)
            result = function(*args, **kwargs)
            activeFunctions.remove(identifier)
            return result
    return wrapper
