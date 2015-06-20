import math

def linear(x, settings = None):
    return x
    
def quadraticInOut(x, settings = None):
    x *= 2
    if x < 1: return x ** 2 / 2
    return 1 - (2 - x) ** 2 / 2
    
def expoEaseOut(x, settings = None):
    return 1 - math.pow(2, -10*x)
def expoEaseIn(x, settings = None):
    return math.pow(2, 10*(x-1))
def quadEaseOut(x, settings = None):
    return -1 * x * (x-2)

def cubicEaseOut(x, settings = None):
    x -= 1
    return x*x*x + 1
def cubicEaseIn(x, settings = None):
    return x*x*x
def cubicEaseInOut(x, settings = None):
    x *= 2
    if x < 1:
        return x*x*x / 2
    x -= 2
    return x*x*x / 2 + 1
    
def backEaseOut(x, back = 1.70158):
    x -= 1
    return x*x*((1 + back)*x+back)+1
def backEaseIn(x, back = 1.70158):
    return x*x*((1 + back)*x-back)
    
def curveInterpolation(x, settings):
    try:
        return (settings[0].evaluate(x) - 0.25)*2
    except:
        settings[1].initialize()
        return (settings[0].evaluate(x) - 0.25)*2
    
def mixedInterpolation(x, settings):
    a, b, factor = settings
    return a[0](x, a[1]) * (1 - factor) + b[0](x, b[1]) * factor