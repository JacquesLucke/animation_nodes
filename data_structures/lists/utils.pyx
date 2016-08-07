from libc.string cimport memmove
from libc.math cimport ceil, floor

cpdef long predictSliceLength(long start, long stop, long step):
    assert step != 0
    cdef long diff = abs(start - stop)
    if start < stop and step > 0: return <long>max(1, ceil(diff / <double>step))
    elif start > stop and step < 0: return <long>max(1, -floor(diff / <double>step))
    else: return 0

cpdef makeStepPositive(long start, long stop, long step):
    cdef long newStart, newEnd, newStep
    if step >= 0:
         newStart, newEnd, newStep = start, stop, step
    elif step < 0:
        newStep = -step

        mod1 = start % newStep
        mod2 = (stop + 1) % newStep
        diff = max(0, mod1 - mod2)

        newStart = stop + diff + 1
        newEnd = start + 1
        newStep = -step
    return newStart, newEnd, newStep

cdef removeValuesInSlice(char* arrayStart, long arrayLength, long elementSize,
                         long start, long stop, long step):
    cdef long removeAmount, i

    if step < 0: start, stop, step = makeStepPositive(start, stop, step)
    removeAmount = predictSliceLength(start, stop, step)

    if step == 1:
        memmove(arrayStart + start * elementSize,
                arrayStart + stop * elementSize,
                arrayLength - stop * elementSize)
    elif step > 1:
        # Move values between the steps
        for i in range(removeAmount - 1):
            memmove(arrayStart + (start + i * (step - 1)) * elementSize,
                    arrayStart + (start + i * step + 1) * elementSize,
                    (step - 1) * elementSize)

        # Move values behind the last step
        memmove(arrayStart + (start + (step - 1) * (removeAmount - 1)) * elementSize,
                arrayStart + (start + (removeAmount - 1) * step + 1) * elementSize,
                arrayLength - (start + (removeAmount - 1) * step + 1) * elementSize)

    return removeAmount
