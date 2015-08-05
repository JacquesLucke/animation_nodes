import time

def measureTime(function):
    def wrapper(*args, **kwargs):
        start = time.clock()
        output = function(*args, **kwargs)
        end = time.clock()
        print("Time: {:.5f} - Function: {}".format(end - start, function.__name__))
        return output
    return wrapper
