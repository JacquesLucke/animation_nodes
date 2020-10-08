from . number cimport lerpFloat

cdef void mixEul3(Euler3* target, Euler3* a, Euler3* b, float factor):
    target.x = lerpFloat(a.x, b.x, factor)
    target.y = lerpFloat(a.y, b.y, factor)
    target.z = lerpFloat(a.z, b.z, factor)
    target.order = a.order
