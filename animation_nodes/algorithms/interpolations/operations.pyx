from ... data_structures cimport DoubleList, InterpolationBase

def sampleInterpolation(InterpolationBase f not None,
                        unsigned int amount,
                        double minValue = 0,
                        double maxValue = 1):

    cdef:
        DoubleList output = DoubleList(length = amount)
        double amplitude = maxValue - minValue
        double factor
        unsigned int i

    if amount >= 2: factor = 1 / (<double>amount - 1)
    else: factor = 0.5

    for i in range(amount):
        output.data[i] = f.evaluate(i * factor) * amplitude + minValue
    return output
