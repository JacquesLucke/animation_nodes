from math import pow, sin, cos, pi, sqrt

'''
Here is a good source for different interpolation functions in Java:
https://github.com/libgdx/libgdx/blob/master/gdx/src/com/badlogic/gdx/math/Interpolation.java
'''

# using pythons functools.partial function is slower
def assignArguments(function, *arguments):
    def interpolationWrapper(x):
        return function(x, *arguments)
    return interpolationWrapper

def getInterpolationPreset(name = "LINEAR", easeIn = True, easeOut = True):
    if not (easeIn or easeOut): return linear
    if name == "LINEAR": return linear
    if name == "SINUSOIDAL":
        if easeIn and easeOut: return sinInOut
        if easeIn: return sinIn
        return sinOut
    if name in exponentOfName.keys():
        if easeIn and easeOut: return assignArguments(powerInOut, exponentOfName[name])
        if easeIn: return assignArguments(powerIn, exponentOfName[name])
        return assignArguments(powerOut, exponentOfName[name])
    if name == "EXPONENTIAL":
        settings = prepareExponentialSettings(base = 2, exponent = 5)
        if easeIn and easeOut: return assignArguments(exponentialInOut, settings)
        if easeIn: return assignArguments(exponentialIn, settings)
        return assignArguments(exponentialOut, settings)
    if name == "CIRCULAR":
        if easeIn and easeOut: return circularInOut
        if easeIn: return circularIn
        return circularOut
    if name == "BACK":
        if easeIn and easeOut: return assignArguments(backInOut, 1.7)
        if easeIn: return assignArguments(backIn, 1.7)
        return assignArguments(backOut, 1.7)
    if name == "BOUNCE":
        settings = prepareBounceSettings(4, 1.5)
        if easeIn and easeOut: return assignArguments(bounceInOut, settings)
        if easeIn: return assignArguments(bounceIn, settings)
        return assignArguments(bounceOut, settings)
    if name == "ELASTIC":
        settings = prepareElasticSettings(base = 1.6, exponent = 6, bounces = 6)
        if easeIn and easeOut: return assignArguments(elasticInOut, settings)
        if easeIn: return assignArguments(elasticIn, settings)
        return assignArguments(elasticOut, settings)

exponentOfName = {
    "QUADRATIC" : 2,
    "CUBIC" : 3,
    "QUARTIC" : 4,
    "QUINTIC" : 5 }

def sampleInterpolation(interpolation, amount = 40, minValue = 0, maxValue = 1):
    samples = []
    size = maxValue - minValue
    for i in range(amount):
          x = i / (amount - 1)
          y = interpolation(x) * size + minValue
          samples.append(y)
    return samples


# Linear interpolation

def linear(x):
    return x


# Power interpolation

def powerInOut(x, exponent = 2):
    '''Exponent has to be a positive integer'''
    if x <= 0.5:
        return pow(x * 2, exponent) / 2
    else:
        return pow((x - 1) * 2, exponent) / (-2 if exponent % 2 == 0 else 2) + 1

def powerIn(x, exponent = 2):
    return pow(x, exponent)

def powerOut(x, exponent = 2):
    return pow(x - 1, exponent) * (-1 if exponent % 2 == 0 else 1) + 1


# Exponential interpolation

def prepareExponentialSettings(base, exponent):
    exponent = min(max(0, int(exponent)), 70)
    base = max(0.0001, base) if base != 1 else 1.0001
    minValue = pow(base, -exponent)
    scale = 1 / (1 - minValue)
    return (base, exponent, minValue, scale)

def exponentialInOut(x, settings):
    base, exponent, minValue, scale = settings
    if x <= 0.5:
        return (pow(base, exponent * (x * 2 - 1)) - minValue) * scale / 2
    else:
        return (2 - (pow(base, -exponent * (x * 2 - 1)) - minValue) * scale) / 2

def exponentialIn(x, settings):
    base, exponent, minValue, scale = settings
    return (pow(base, exponent * (x - 1)) - minValue) * scale

def exponentialOut(x, settings):
    base, exponent, minValue, scale = settings
    return 1 - (pow(base, -exponent * x) - minValue) * scale


# Circle interpolation

def circularInOut(x):
    if x <= 0.5:
        x *= 2
        return (1 - sqrt(1 - x * x)) / 2
    else:
        x = (x - 1) * 2
        return (sqrt(1 - x * x) + 1) / 2

def circularIn(x):
    return 1 - sqrt(1 - x * x)

def circularOut(x):
    x -= 1
    return sqrt(1 - x * x)


# Elastic interpolation

def prepareElasticSettings(base, exponent, bounces):
    scale = -1 if bounces % 2 == 0 else 1
    bounces = bounces + 0.5
    base = max(base, 0)
    bounces = bounces * pi * (1 if bounces % 2 == 0 else -1)
    return (base, exponent, bounces, scale)


def elasticInOut(x, settings):
    base, exponent, bounces, scale = settings
    if x <= 0.5:
        x *= 2
        return pow(base, exponent * (x - 1)) * sin(x * bounces) * scale / 2
    else:
        x = (1 - x) * 2
        return 1 - pow(base, exponent * (x - 1)) * sin(x * bounces) * scale / 2

def elasticIn(x, settings):
    base, exponent, bounces, scale = settings
    return pow(base, exponent * (x - 1)) * sin(x * bounces) * scale

def elasticOut(x, settings):
    base, exponent, bounces, scale = settings
    x = 1 - x
    return 1 - pow(base, exponent * (x - 1)) * sin(x * bounces) * scale


# Bounce interpolation

def prepareBounceSettings(bounces, base):
    '''
    sum(widths) - widths[0] / 2 = 1
    '''
    bounces = max(1, int(bounces))
    a = 2 ** (bounces - 1)
    b = 2 ** bounces - 2 ** (bounces - 2) - 1
    c = a / b
    widths = [c / 2 ** i for i in range(bounces)]
    heights = [x * base for x in widths]
    heights[0] = 1
    return (widths, heights)

def bounceInOut(x, settings):
    if x <= 0.5: return (1 - bounceOut(1 - x * 2, settings)) / 2
    else: return bounceOut(x * 2 - 1, settings) / 2 + 0.5

def bounceIn(x, settings):
    return 1 - bounceOut(1 - x, settings)

def bounceOut(x, settings):
    widths, heights = settings
    x += widths[0] / 2
    for width, height in zip(widths, heights):
        if x <= width: break
        x -= width
    x /= width
    z = 4 / width * height * x
    return 1 -(z - z * x) * width



# Back swing interpolation

def backInOut(x, scale = 1.7):
    if x <= 0.5:
        x *= 2
        return x * x * ((scale + 1) * x - scale) / 2
    else:
        x = (x - 1) * 2
        return x * x * ((scale + 1) * x + scale) / 2 + 1

def backIn(x, scale = 1.7):
    return x * x * ((scale + 1) * x - scale)

def backOut(x, scale = 1.7):
    x -= 1
    return x * x * ((scale + 1) * x + scale) + 1


# Sine interpolation

def sinInOut(x):
    return (1 - cos(x * pi)) / 2

def sinIn(x):
    return 1 - cos(x * pi / 2)

def sinOut(x):
    return sin(x * pi / 2)


# Specials

def fCurveMapping(x, settings):
    fCurve, xMove, xFactor, yMove, yDivisor = settings
    x = x * xFactor + xMove
    return (fCurve.evaluate(x) + yMove) / yDivisor

def mixedInterpolation(x, settings):
    a, b, factor = settings
    return a(x) * (1 - factor) + b(x) * factor
