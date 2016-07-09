from libc.math cimport ceil, floor

cpdef long predictRangeLength(long start, long end, long step):
    assert step != 0
    cdef long diff = abs(start - end)
    if start < end and step > 0: return <long>ceil(diff / step)
    elif start > end and step < 0: return -<long>floor(diff / step)
    else: return 0
