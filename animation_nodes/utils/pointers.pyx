from libc.stdint cimport intptr_t

cdef void *intToPointer(number):
    return <void*><intptr_t>number

cdef object pointerToInt(void *pointer):
    return <intptr_t>pointer
