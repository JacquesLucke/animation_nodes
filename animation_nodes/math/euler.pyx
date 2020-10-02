from . number cimport lerp

cdef void mixEul3(Euler3* target, Euler3* a, Euler3* b, float factor):
    target.x = lerp(a.x, b.x, factor)
    target.y = lerp(a.y, b.y, factor)
    target.z = lerp(a.z, b.z, factor)
