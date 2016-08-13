from libc.math cimport floor

cdef void calcSegmentIndicesAndFactor(long amount, bint cyclic, float parameter, long* index, float* factor):
    if not cyclic:
        if parameter < 1:
            index[0] = <long>floor(parameter * (amount - 1))
            index[1] = index[0] + 1
            factor[0] = parameter * (amount - 1) - index[0]
        else:
            index[0] = amount - 2
            index[1] = amount - 1
            factor[0] = 1
    else:
        if parameter < 1:
            index[0] = <long>floor(parameter * amount)
            index[1] = index[0] + 1 if index[0] < (amount - 1) else 0
            factor[0] = parameter * amount - index[0]
        else:
            index[0] = amount - 1
            index[1] = 0
            factor[0] = 1
