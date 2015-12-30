import time
from .. preferences import debuggingIsEnabled

def prettyTime(seconds):
    if seconds > 1.5: return "{:.2f} s".format(seconds)
    else: return "{:.5f} ms".format(seconds * 1000)

def measureTime(function):
    def wrapper(*args, **kwargs):
        start = time.clock()
        output = function(*args, **kwargs)
        end = time.clock()
        duration = end - start
        if debuggingIsEnabled():
            print("Time: {:.5f} - fps : {:.2f} - Function: {}".format(duration, 1 / max(duration, 1e-10), function.__name__))
        return output
    return wrapper
