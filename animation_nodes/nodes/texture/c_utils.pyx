# cython: profile=True
from ... data_structures cimport (
    Color,
    ColorList,
    DoubleList,
    Vector3DList
)

def getTextureColors(texture, Vector3DList locations):
    cdef long amount = locations.length
    cdef DoubleList reds = DoubleList(length = amount)
    cdef DoubleList greens = DoubleList(length = amount)
    cdef DoubleList blues = DoubleList(length = amount)
    cdef DoubleList alphas = DoubleList(length = amount)
    cdef ColorList colors = ColorList(length = amount)
    cdef float r, g, b, a

    for i in range(amount):
        r, g, b, a = texture.evaluate(locations[i])
        reds.data[i] = r
        greens.data[i] = g
        blues.data[i] = b
        alphas.data[i] = a
        colors.data[i] = Color(r, g, b, a)
    return colors, reds, greens, blues, alphas
