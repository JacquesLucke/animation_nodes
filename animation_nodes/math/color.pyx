from . color cimport Color

cdef void addColor(Color* target, Color* a, Color* b):
  target.r = a.r + b.r
  target.g = a.g + b.g
  target.b = a.b + b.b
  target.a = a.a + b.a

cdef void scaleColor_Inplace(Color* c, float factor):
  c.r *= factor
  c.g *= factor
  c.b *= factor
  c.a *= factor

    