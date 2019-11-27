from ... data_structures cimport (
    ColorList,
    VirtualColorList,
    PolygonIndicesList
)

def getLoopColorsFromVertexColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef long i
    cdef Amount = len(polygons.indices)
    cdef ColorList loopsColors = ColorList(length = Amount)

    for i in range(Amount):
        loopsColors.data[i] = colors.get(polygons.indices[i])[0]
    return loopsColors
    
def getLoopColorsFromPolygonColors(PolygonIndicesList polygons, VirtualColorList colors):
    cdef long i, j, index
    cdef ColorList loopsColors = ColorList(length = len(polygons.indices))
    
    index = 0 
    for i in range(len(polygons)):
        for j in range(polygons.polyLengths[i]):
            loopsColors.data[index] = colors.get(i)[0]
            index += 1
    return loopsColors
    
