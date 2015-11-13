def formatVector(vector):
    return "V({:>8.4f}, {:>8.4f}, {:>8.4f})".format(*vector)

def formatEuler(euler):
    return "E({:>8.4f}, {:>8.4f}, {:>8.4f})".format(*euler)

def formatQuaternion(quaternion):
    return "Q({:>7.4f}, {:>7.4f}, {:>7.4f}, {:>7.4f})".format(*quaternion)

def formatFloat(number):
    return "{:>10.5f}".format(number)
