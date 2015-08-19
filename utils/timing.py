import time

def measureTime(function):
    def wrapper(*args, **kwargs):
        start = time.clock()
        output = function(*args, **kwargs)
        end = time.clock()
        duration = end - start
        print("Time: {:.5f} - fps : {:.2f} - Function: {}".format(duration, 1 / duration, function.__name__))
        return output
    return wrapper
