cdef struct Euler3:
    float x, y, z
    char order
    # char[3] pad

cdef void mixEul3(Euler3* target, Euler3* a, Euler3* b, float factor)
