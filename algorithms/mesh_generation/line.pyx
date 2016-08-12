from ... data_structures cimport Vector3DList, EdgeIndicesList

# Vertices
###########################################

def vertices(start, end, long steps):
    assert steps >= 2
    cdef:
        float _start[3]
        float _end[3]
        float stepsInverse = 1 / <float>(steps - 1)
        float startWeight, endWeight
        long i

    _start = start
    _end = end

    vertices = Vector3DList(length = steps)
    for i in range(steps):
        startWeight = 1 - i * stepsInverse
        endWeight = i * stepsInverse
        vertices.base.data[i * 3 + 0] = _start[0] * startWeight + _end[0] * endWeight
        vertices.base.data[i * 3 + 1] = _start[1] * startWeight + _end[1] * endWeight
        vertices.base.data[i * 3 + 2] = _start[2] * startWeight + _end[2] * endWeight
    return vertices


# Edges
############################################

def edges(long steps):
    edges = EdgeIndicesList(length = steps - 1)
    cdef long i
    for i in range(steps - 1):
        edges.base.data[i * 2 + 0] = i
        edges.base.data[i * 2 + 1] = i + 1
    return edges
