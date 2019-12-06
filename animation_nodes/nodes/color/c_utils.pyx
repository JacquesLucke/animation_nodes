import cython
from ... math cimport (
    addColor,
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
    cdef loopsCount = len(polygons.indices)
    cdef ColorList loopsColors = ColorList(length = loopsCount)

    cdef long i
    for i in range(loopsCount):
        loopsColors.data[i] = colors.get(polygons.indices[i])[0]
    return loopsColors
    
def getLoopColorsFromPolygonColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef ColorList loopsColors = ColorList(length = len(polygons.indices))
    
    cdef long i, j, index
    cdef Color polygonColor
    index = 0 
    for i in range(len(polygons)):
        polygonColor = colors.get(i)[0]
        for j in range(polygons.polyLengths[i]):
            loopsColors.data[index] = polygonColor
            index += 1
    return loopsColors

@cython.cdivision(True)
def getVertexColorsFromLoopColors(long vertexCount, PolygonIndicesList polygons, VirtualColorList colors):
    cdef ColorList vertexsColors = ColorList.fromValue((0.0, 0.0, 0.0, 0.0), length = vertexCount)
    cdef LongList loopCounts = LongList.fromValue(0, length = vertexCount)        
    
    cdef long i, index
    for i in range(len(polygons.indices)):
        index = polygons.indices[i]
        addColor_Inplace(vertexsColors.data + index, colors.get(index))
        loopCounts[index] += 1

    for i in range(vertexCount):
        scaleColor_Inplace(vertexsColors.data + i, 1.0 / loopCounts[i])
    return vertexsColors

@cython.cdivision(True)
def getPolygonColorsFromLoopColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef polygonsCount = len(polygons)
    cdef ColorList polygonsColors = ColorList.fromValue((0.0, 0.0, 0.0, 0.0), length = polygonsCount)
    
    cdef long i, j, index, polyLength
    index = 0 
    for i in range(polygonsCount):
        polyLength = polygons.polyLengths[i]
        for j in range(polyLength):
            addColor_Inplace(polygonsColors.data + i, colors.get(polygons.indices[index]))
            index += 1
        scaleColor_Inplace(polygonsColors.data + i, 1.0 / polyLength)
    return polygonsColors

