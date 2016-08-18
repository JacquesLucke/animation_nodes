from . implementations import *

def getInterpolationPreset(str name = "LINEAR", bint easeIn, bint easeOut):
    if not (easeIn or easeOut): return Linear()
