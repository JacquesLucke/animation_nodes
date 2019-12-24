cdef struct Color:
    float r, g, b, a

cdef void addColor(Color* target, Color* a, Color* b)
cdef void addColor_Inplace(Color* c, Color* a)
cdef void scaleColor_Inplace(Color* c, float factor)

