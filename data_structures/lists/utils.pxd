cpdef long predictSliceLength(long start, long end, long step)
cpdef makeStepPositive(long start, long stop, long step)

cdef removeValuesInSlice(char* arrayStart, long arrayLength, long elementSize,
                         long start, long stop, long step)

cdef getValuesInSlice(void* source, Py_ssize_t elementAmount, int elementSize,
                      void** target, Py_ssize_t* targetLength,
                      sliceObject)
