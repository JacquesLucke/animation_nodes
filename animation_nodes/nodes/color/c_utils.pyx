import cython
from ... math cimport (
    addColor_Inplace,
    scaleColor_Inplace,
    hsva_to_rgba,
    hsla_to_rgba,
    yiqa_to_rgba,
)
from ... data_structures cimport (
    Color,
    LongList,
    FloatList,
    ColorList,
    VirtualColorList,
    VirtualDoubleList,
    PolygonIndicesList
)


def colorListFromRGBA(Py_ssize_t amount, VirtualDoubleList r, VirtualDoubleList g,
                      VirtualDoubleList b, VirtualDoubleList a):
    cdef ColorList output = ColorList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        output.data[i].r = <float>r.get(i)
        output.data[i].g = <float>g.get(i)
        output.data[i].b = <float>b.get(i)
        output.data[i].a = <float>a.get(i)
    return output

def colorListFromHSVA(Py_ssize_t amount, VirtualDoubleList h, VirtualDoubleList s,
                      VirtualDoubleList v, VirtualDoubleList a):
    cdef ColorList output = ColorList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        hsva_to_rgba(output.data + i, <float>h.get(i), <float>s.get(i),
                                      <float>v.get(i), <float>a.get(i))
    return output

def colorListFromHSLA(Py_ssize_t amount, VirtualDoubleList h, VirtualDoubleList s,
                      VirtualDoubleList l, VirtualDoubleList a):
    cdef ColorList output = ColorList(length = amount)
    cdef Py_ssize_t i
    for i in range(amount):
        hsla_to_rgba(output.data + i, <float>h.get(i), <float>s.get(i),
                                      <float>l.get(i), <float>a.get(i))
    return output

def colorListFromYIQA(Py_ssize_t amount, VirtualDoubleList y, VirtualDoubleList i,
                      VirtualDoubleList q, VirtualDoubleList a):
    cdef ColorList output = ColorList(length = amount)
    cdef Py_ssize_t j
    for j in range(amount):
        yiqa_to_rgba(output.data + j, <float>y.get(j), <float>i.get(j),
                                      <float>q.get(j), <float>a.get(j))
    return output

def getLoopColorsFromVertexColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef long loopsCount = polygons.indices.length
    cdef ColorList loopsColors = ColorList(length = loopsCount)

    cdef long i
    for i in range(loopsCount):
        loopsColors.data[i] = colors.get(polygons.indices.data[i])[0]
    return loopsColors

def getLoopColorsFromPolygonColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef ColorList loopsColors = ColorList(length = polygons.indices.length)

    cdef long i, j, index
    cdef Color polygonColor
    index = 0
    for i in range(polygons.getLength()):
        polygonColor = colors.get(i)[0]
        for j in range(polygons.polyLengths.data[i]):
            loopsColors.data[index] = polygonColor
            index += 1
    return loopsColors

@cython.cdivision(True)
def getVertexColorsFromLoopColors(long vertexCount, PolygonIndicesList polygons, VirtualColorList colors):
    cdef ColorList vertexColors = ColorList(length = vertexCount)
    cdef LongList loopCounts = LongList(length = vertexCount)
    loopCounts.fill(0)
    vertexColors.fill(0)

    cdef long i, index
    for i in range(polygons.indices.length):
        index = polygons.indices.data[i]
        addColor_Inplace(vertexColors.data + index, colors.get(i))
        loopCounts.data[index] += 1

    for i in range(vertexCount):
        scaleColor_Inplace(vertexColors.data + i, 1.0 / loopCounts.data[i])
    return vertexColors

@cython.cdivision(True)
def getPolygonColorsFromLoopColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef long polygonCount = polygons.getLength()
    cdef ColorList polygonColors = ColorList(length = polygonCount)
    polygonColors.fill(0)

    cdef long i, j, index, polyLength
    index = 0
    for i in range(polygonCount):
        polyLength = polygons.polyLengths.data[i]
        for j in range(polyLength):
            addColor_Inplace(polygonColors.data + i, colors.get(index))
            index += 1
        scaleColor_Inplace(polygonColors.data + i, 1.0 / polyLength)
    return polygonColors

@cython.cdivision(True)
def offsetColors(ColorList colors, VirtualColorList offsets, FloatList influences, str method = "ADD"):
    cdef Color *offset
    cdef float influence
    cdef Py_ssize_t i

    if method == "ADD":
        for i in range(colors.length):
            influence = influences.data[i]
            offset = offsets.get(i)
            colors.data[i].r += offset.r * influence
            colors.data[i].g += offset.g * influence
            colors.data[i].b += offset.b * influence
            colors.data[i].a += offset.a * influence
    elif method == "SUBTRACT":
        for i in range(colors.length):
            influence = influences.data[i]
            offset = offsets.get(i)
            colors.data[i].r -= offset.r * influence
            colors.data[i].g -= offset.g * influence
            colors.data[i].b -= offset.b * influence
            colors.data[i].a -= offset.a * influence
    elif method == "MULTIPLY":
        for i in range(colors.length):
            influence = influences.data[i]
            offset = offsets.get(i)
            colors.data[i].r *= offset.r * influence
            colors.data[i].g *= offset.g * influence
            colors.data[i].b *= offset.b * influence
            colors.data[i].a *= offset.a * influence
    elif method == "DIVIDE":
        for i in range(colors.length):
            influence = influences.data[i]
            offset = offsets.get(i)
            colors.data[i].r /= offset.r * influence
            colors.data[i].g /= offset.g * influence
            colors.data[i].b /= offset.b * influence
            colors.data[i].a /= offset.a * influence
    elif method == "MIX":
        for i in range(colors.length):
            influence = influences.data[i]
            offset = offsets.get(i)
            colors.data[i].r = lerp(colors.data[i].r, offset.r, influence)
            colors.data[i].g = lerp(colors.data[i].g, offset.g, influence)
            colors.data[i].b = lerp(colors.data[i].b, offset.b, influence)
            colors.data[i].a = lerp(colors.data[i].a, offset.a, influence)

cdef lerp(float x, float y, float p):
    return (1.0 - p) * x + p * y
