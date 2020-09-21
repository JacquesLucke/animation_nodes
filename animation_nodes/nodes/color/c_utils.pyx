import cython
from ... algorithms.random_number_generators cimport XoShiRo256Plus
from ... math cimport (
    addColor_Inplace,
    scaleColor_Inplace,
    hsva_to_rgba,
    hsla_to_rgba,
    yiqa_to_rgba,
    rgba_to_hsva,
    rgba_to_hsla,
    rgba_to_yiqa,
)
from ... data_structures cimport (
    Color,
    LongList,
    FloatList,
    ColorList,
    DoubleList,
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

def RGBAFromColorList(ColorList colorList):
    cdef DoubleList r = DoubleList(length = colorList.length)
    cdef DoubleList g = DoubleList(length = colorList.length)
    cdef DoubleList b = DoubleList(length = colorList.length)
    cdef DoubleList a = DoubleList(length = colorList.length)
    cdef Py_ssize_t i
    for i in range(colorList.length):
        r.data[i] = <double>colorList.data[i].r
        g.data[i] = <double>colorList.data[i].g
        b.data[i] = <double>colorList.data[i].b
        a.data[i] = <double>colorList.data[i].a
    return r, g, b, a

def HSVAFromColorList(ColorList colorList):
    cdef DoubleList h = DoubleList(length = colorList.length)
    cdef DoubleList s = DoubleList(length = colorList.length)
    cdef DoubleList v = DoubleList(length = colorList.length)
    cdef DoubleList a = DoubleList(length = colorList.length)
    cdef Py_ssize_t i
    for i in range(colorList.length):
        rgba_to_hsva(colorList.data + i, h.data + i, s.data + i,
                     v.data + i, a.data + i)
    return h, s, v, a

def HSLAFromColorList(ColorList colorList):
    cdef DoubleList h = DoubleList(length = colorList.length)
    cdef DoubleList s = DoubleList(length = colorList.length)
    cdef DoubleList l = DoubleList(length = colorList.length)
    cdef DoubleList a = DoubleList(length = colorList.length)
    cdef Py_ssize_t i
    for i in range(colorList.length):
        rgba_to_hsla(colorList.data + i, h.data + i, s.data + i,
                     l.data + i, a.data + i)
    return h, s, l, a

def YIQAFromColorList(ColorList colorList):
    cdef DoubleList y = DoubleList(length = colorList.length)
    cdef DoubleList i = DoubleList(length = colorList.length)
    cdef DoubleList q = DoubleList(length = colorList.length)
    cdef DoubleList a = DoubleList(length = colorList.length)
    cdef Py_ssize_t j
    for j in range(colorList.length):
        rgba_to_yiqa(colorList.data + j, y.data + j, i.data + j,
                     q.data + j, a.data + j)
    return y, i, q, a

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

def generateRandomColors(Py_ssize_t seed, Py_ssize_t count):
    cdef Py_ssize_t i
    cdef XoShiRo256Plus rng = XoShiRo256Plus(seed)
    cdef ColorList colors = ColorList(length = count)

    for i in range(count):
        colors.data[i].r = rng.nextFloat()
        colors.data[i].g = rng.nextFloat()
        colors.data[i].b = rng.nextFloat()
        colors.data[i].a = 1.0

    return colors
