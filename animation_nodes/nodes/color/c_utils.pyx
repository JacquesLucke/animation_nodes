# cython: profile=True
cimport cython

from ... data_structures cimport (
    ColorList,
    VirtualColorList,
    PolygonIndicesList
)

def loopsColorsList(long Amount, PolygonIndicesList polygons, VirtualColorList colors, 
                    ColorList loopsColors):
    cdef long i
    for i in range(Amount):
        loopsColors[i] = colors[polygons.indices[i]]
    return loopsColors
    
def polygonsColorsList(long Amount, PolygonIndicesList polygons, VirtualColorList colors,
                       ColorList polygonsColors):
    cdef long i, j, index
    cdef long polygonsAmount = len(polygons)
    index = 0    
    for i in range(polygonsAmount):
        for j in range(len(polygons[i])):
            polygonsColors[index] = colors[i]
            index += 1
    return polygonsColors
    