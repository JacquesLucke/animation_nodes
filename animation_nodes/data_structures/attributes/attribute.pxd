cdef enum AttributeType:
    UVMAP, MATERIAL_INDEX, VERTEX_COLOR, CUSTOM
cdef enum AttributeDomain:
    POINT, EDGE, POLYGON, CORNER
cdef enum AttributeDataType:
    INT, FLOAT, FLOAT2, FLOAT_VECTOR, FLOAT_COLOR, BYTE_COLOR, BOOLEAN

cdef class Attribute:
    cdef:
        public str name
        public AttributeType type
        public AttributeDomain domain
        public AttributeDataType dataType
        public object data
