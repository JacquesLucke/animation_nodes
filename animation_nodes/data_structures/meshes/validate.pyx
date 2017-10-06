from libc.stdint cimport uint32_t

from .. lists.polygon_indices_list cimport PolygonIndicesList
from .. lists.base_lists cimport (
    UIntegerList, EdgeIndices, IntegerList,
    Vector3DList, EdgeIndicesList
)

def checkMeshData(Vector3DList vertices, EdgeIndicesList edges, PolygonIndicesList polygons):
    if edges.length > 0 and edges.getMaxIndex() >= vertices.length:
        raise Exception("there is an edge that references a not existing vertex")
    if polygons.getLength() > 0 and polygons.getMaxIndex() >= vertices.length:
        raise Exception("there is a polygon that references a not existing vertex")

    checkIndividualEdgeVadility(edges)
    checkIndividualPolygonValidity(polygons)

    cdef UIntegerList edgeHashes = getEdgeHashes(edges)
    cdef UIntegerList polygonHashes = getPolygonHashes(polygons)

    cdef IntegerList edgesLookup = getLookupForEdgeHashes(edgeHashes, edges, ignoreDuplicates = False)
    cdef IntegerList polygonsLookup = getLookupForPolygonHashes(polygonHashes, polygons)

    checkIfAllRequiredEdgesExist(polygons, edges, edgeHashes, edgesLookup)


# Check individual edges/polygons
####################################################

def checkIndividualEdgeVadility(EdgeIndicesList edges):
    cdef Py_ssize_t i
    cdef EdgeIndices *_edges = edges.data
    for i in range(edges.length):
        if _edges[i].v1 == _edges[i].v2:
            raise Exception("Vertex cannot be connected to itself (index: {}, value: {})"
                            .format(i, edges[i]))

def checkIndividualPolygonValidity(PolygonIndicesList polygons):
    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length
    cdef bint invalid

    cdef Py_ssize_t i, j, k
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        if length == 3:
            invalid = (indices[start+0] == indices[start+1]
                    or indices[start+0] == indices[start+2]
                    or indices[start+1] == indices[start+2])
        elif length == 4:
            invalid = (indices[start+0] == indices[start+1]
                    or indices[start+0] == indices[start+2]
                    or indices[start+0] == indices[start+3]
                    or indices[start+1] == indices[start+2]
                    or indices[start+1] == indices[start+3]
                    or indices[start+2] == indices[start+3])
        else:
            invalid = False
            for j in range(start, start + length - 1):
                for k in range(start + j + 1, start + length):
                    invalid = invalid or (indices[j] == indices[k])

        if invalid:
            raise Exception("Polygon cannot use a Vertex twice (index: {}, value: {})"
                            .format(i, polygons[i]))

# Edge/Polygon relations
####################################################

def checkIfAllRequiredEdgesExist(PolygonIndicesList polygons, EdgeIndicesList edges,
                                 UIntegerList edgeHashes, IntegerList edgesLookup):
    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef unsigned int mask = edgesLookup.length - 1

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            if not edgeExistsInLookup(indices[j], indices[j+1], edges.data, edgesLookup.data, mask):
                raise Exception("an edge is not available for polygon {}".format(i))

        if not edgeExistsInLookup(indices[start], indices[start + length - 1], edges.data, edgesLookup.data, mask):
            raise Exception("an edge is not available for polygon {}".format(i))

def calculateLoopEdges(EdgeIndicesList edges, PolygonIndicesList polygons):
    cdef UIntegerList edgeHashes = getEdgeHashes(edges)
    cdef IntegerList edgesLookup = getLookupForEdgeHashes(edgeHashes, edges)

    cdef UIntegerList result = UIntegerList(length = polygons.indices.length)

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length
    cdef unsigned int mask = edgesLookup.length - 1

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            result.data[j] = getEdgeIndex(indices[j], indices[j+1], edges.data, edgesLookup.data, mask)

        result.data[start+length-1] = getEdgeIndex(indices[start], indices[start + length - 1], edges.data, edgesLookup.data, mask)

    return result

def createValidEdgesList(EdgeIndicesList edges, PolygonIndicesList polygons):
    cdef EdgeIndicesList allEdges = edges + getAllPolygonEdges(polygons)
    cdef UIntegerList edgeHashes = getEdgeHashes(allEdges)
    cdef IntegerList edgesLookup = getLookupForEdgeHashes(edgeHashes, allEdges, ignoreDuplicates = True)

    cdef EdgeIndicesList newEdges = EdgeIndicesList(capacity = allEdges.length)
    cdef Py_ssize_t index = 0
    cdef Py_ssize_t i
    for i in range(edgesLookup.length):
        if edgesLookup.data[i] >= 0:
            newEdges.data[index] = allEdges.data[edgesLookup.data[i]]
            index += 1
    newEdges.length = index
    newEdges.shrinkToLength()
    return newEdges

def getAllPolygonEdges(PolygonIndicesList polygons):
    cdef EdgeIndicesList edges = EdgeIndicesList(length = polygons.indices.length)

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, j
    cdef Py_ssize_t index = 0
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]

        for j in range(start, start + length - 1):
            edges.data[index].v1 = indices[j]
            edges.data[index].v2 = indices[j+1]
            index += 1

        edges.data[index].v1 = indices[start]
        edges.data[index].v2 = indices[start + length - 1]
        index += 1

    return edges


# Compute edge/polygon hashes
####################################################

def getEdgeHashes(EdgeIndicesList edges):
    cdef UIntegerList hashes = UIntegerList(length = edges.length)
    cdef unsigned int *_hashes = hashes.data
    cdef EdgeIndices *_edges = edges.data
    cdef Py_ssize_t i
    for i in range(edges.length):
        _hashes[i] = hashUInt(_edges[i].v1) ^ hashUInt(_edges[i].v2)
    return hashes

def getPolygonHashes(PolygonIndicesList polygons):
    cdef UIntegerList hashes = UIntegerList(length = polygons.getLength())
    cdef unsigned int *_hashes = hashes.data

    cdef unsigned int *indices = polygons.indices.data
    cdef unsigned int *polyStarts = polygons.polyStarts.data
    cdef unsigned int *polyLengths = polygons.polyLengths.data
    cdef unsigned int start, length

    cdef Py_ssize_t i, j
    for i in range(polygons.getLength()):
        start = polyStarts[i]
        length = polyLengths[i]
        if length == 3:
            _hashes[i] = hashUInt(indices[start]) ^ hashUInt(indices[start+1]) ^ hashUInt(indices[start+2])
        elif length == 4:
            _hashes[i] = hashUInt(indices[start]) ^ hashUInt(indices[start+1]) ^ hashUInt(indices[start+2]) ^ hashUInt(indices[start+3])
        else:
            _hashes[i] = 0
            for j in range(start, start + length):
                _hashes[i] ^= hashUInt(indices[j])

    return hashes

cdef inline uint32_t hashUInt(uint32_t x):
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = ((x >> 16) ^ x) * 0x45d9f3b
    x = (x >> 16) ^ x
    return x




# Create lookup-table for edges/polygons
####################################################

ctypedef char (*HandleDuplicateFunction)(void *settings, unsigned int i1, unsigned int i2)

cdef struct PolygonListData:
    unsigned int *indices
    unsigned int *polyStarts
    unsigned int *polyLengths

def getLookupForEdgeHashes(UIntegerList hashes, EdgeIndicesList edges, bint ignoreDuplicates = False):
    if ignoreDuplicates:
        return createLookupForHashes(hashes, compareEdges_IgnoreDuplicate, edges.data)
    else:
        return createLookupForHashes(hashes, compareEdges_FailOnDuplicate, edges.data)

def getLookupForPolygonHashes(UIntegerList hashes, PolygonIndicesList polygons):
    cdef PolygonListData data
    data.indices = polygons.indices.data
    data.polyStarts = polygons.polyStarts.data
    data.polyLengths = polygons.polyLengths.data
    return createLookupForHashes(hashes, comparePolygons, &data)

cdef inline char edgeExistsInLookup(unsigned int i1, unsigned int i2,
                                  EdgeIndices *edges, int *edgesLookup,
                                  unsigned int mask):
    return getEdgeIndex(i1, i2, edges, edgesLookup, mask) >= 0

cdef inline Py_ssize_t getEdgeIndex(unsigned int i1, unsigned int i2,
                                    EdgeIndices *edges, int *edgesLookup,
                                    unsigned int mask):
    cdef unsigned int slot = (hashUInt(i1) ^ hashUInt(i2)) & mask
    cdef int index
    while True:
        index = edgesLookup[slot]
        if index < 0:
            return -1
        if (edges[index].v1 == i1 and edges[index].v2 == i2) or (edges[index].v1 == i2 and edges[index].v2 == i1):
            return index
        slot = (slot + 1) & mask


cdef createLookupForHashes(UIntegerList hashes,
                         HandleDuplicateFunction handleDuplicate, void *settings):
    cdef Py_ssize_t maskSize = max(hashes.length-1, 0).bit_length() + 1
    cdef Py_ssize_t indexSize = 2 ** maskSize
    cdef unsigned int mask = indexSize - 1 # produces something like ...00011111

    cdef IntegerList lookup = IntegerList.fromValue(-1, length = indexSize)
    cdef int *_lookup = lookup.data


    cdef Py_ssize_t i, indexInSlot
    cdef unsigned int slot, currentHash
    cdef char duplicateType

    for i in range(hashes.length):
        currentHash = hashes.data[i]

        slot = currentHash & mask
        indexInSlot = _lookup[slot]

        while indexInSlot >= 0:
            if currentHash == hashes.data[indexInSlot]:
                duplicateType = handleDuplicate(settings, i, indexInSlot)
                if duplicateType == 0:
                    pass # no real duplicate, just same hashes
                if duplicateType == 1:
                    break # ignore duplicate
                elif duplicateType == 2:
                    raise Exception("duplicates at {} and {}".format(i, indexInSlot))

            slot = (slot + 1) & mask
            indexInSlot = _lookup[slot]

        _lookup[slot] = i


    return lookup


cdef char compareEdges_FailOnDuplicate(void *settings, unsigned int i1, unsigned int i2):
    return 2 if areEdgesEqual(settings, i1, i2) else 0

cdef char compareEdges_IgnoreDuplicate(void *settings, unsigned int i1, unsigned int i2):
    return 1 if areEdgesEqual(settings, i1, i2) else 0

cdef inline char areEdgesEqual(void *settings, unsigned int i1, unsigned int i2):
    cdef EdgeIndices *edges = <EdgeIndices*>settings
    return ((edges[i1].v1 == edges[i2].v1 and edges[i1].v2 == edges[i2].v2)
         or (edges[i1].v1 == edges[i2].v2 and edges[i1].v2 == edges[i2].v1))


cdef char comparePolygons(void *settings, unsigned int i1, unsigned int i2):
    cdef PolygonListData *data = <PolygonListData*>settings
    cdef unsigned int *indices = data.indices
    cdef unsigned int *polyStarts = data.polyStarts
    cdef unsigned int *polyLengths = data.polyLengths

    # First compare lengths
    cdef unsigned int length1 = polyLengths[i1]
    cdef unsigned int length2 = polyLengths[i2]
    if length1 != length2:
        return 0
    cdef unsigned int length = length1

    # Then calculate a simple hash using a commutative operations
    # this way we don't have to sort the indices most of the time
    cdef unsigned int s1 = polyStarts[i1]
    cdef unsigned int s2 = polyStarts[i2]
    cdef unsigned int sum1, sum2
    cdef Py_ssize_t i

    if length == 3:
        sum1 = indices[s1+0] + indices[s1+1] + indices[s1+2]
        sum2 = indices[s2+0] + indices[s2+1] + indices[s2+2]
    elif length == 4:
        sum1 = indices[s1+0] + indices[s1+1] + indices[s1+2] + indices[s1+3]
        sum2 = indices[s2+0] + indices[s2+1] + indices[s2+2] + indices[s2+3]
    else:
        sum1 = sum2 = 0
        for i in range(s1, s1 + length):
            sum1 += indices[i]
        for i in range(s2, s2 + length):
            sum2 += indices[i]

    # do real comparison if length and sum are equal
    if sum1 == sum2:
        p1 = [indices[i] for i in range(s1, s1 + length)]
        p2 = [indices[i] for i in range(s2, s2 + length)]
        if set(p1) == set(p2):
            return 2

    return 0
