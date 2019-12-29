import cython
from ... math cimport (
    addColor_Inplace,
    scaleColor_Inplace
)
from ... data_structures cimport (
    Color,
    LongList,
    ColorList,
    VirtualColorList,
    PolygonIndicesList
)

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

