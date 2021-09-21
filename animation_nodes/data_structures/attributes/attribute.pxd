from .. lists.clist cimport CList

cpdef enum AttributeType:
    MATERIAL_INDEX,
    UV_MAP,
    VERTEX_COLOR,
    BEVEL_VERTEX_WEIGHT,
    BEVEL_EDGE_WEIGHT,
    EDGE_CREASE,
    CUSTOM,

cpdef enum AttributeDomain:
    POINT,
    EDGE,
    FACE,
    CORNER,

cpdef enum AttributeDataType:
    INT,
    FLOAT,
    FLOAT2,
    FLOAT_VECTOR,
    FLOAT_COLOR,
    BYTE_COLOR,
    BOOLEAN,

cdef class Attribute:
    cdef:
        readonly str name
        readonly AttributeType type
        readonly AttributeDomain domain
        readonly AttributeDataType dataType
        readonly CList data
