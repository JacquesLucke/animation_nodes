from .. lists.base_lists cimport (
    LongList,
    FloatList,
    ColorList,
    BooleanList,
    Vector2DList,
    Vector3DList,
)

cdef class Attribute:
    def __cinit__(self, str name = None,
                        AttributeType type = CUSTOM,
                        AttributeDomain domain = POINT,
                        AttributeDataType dataType = FLOAT,
                        object data = None):

        self.name = name
        self.type = type
        self.domain = domain
        self.dataType = dataType
        self.data = data

    def copy(self):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.copy())

    def repeated(self, Py_ssize_t amount = -1):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.repeated(amount = amount))

    def extend(self, object data):
        self.data.extend(data)

    def getTypeAsString(self):
        if self.type == UV_MAP:
            return "UV_MAP"
        elif self.type == MATERIAL_INDEX:
            return "MATERIAL_INDEX"
        elif self.type == VERTEX_COLOR:
            return "VERTEX_COLOR"
        return "CUSTOM"

    def getDomainAsString(self):
        if self.domain == POINT:
            return "POINT"
        elif self.domain == EDGE:
            return "EDGE"
        elif self.domain == POLYGON:
            return "POLYGON"
        return "CORNER"

    def getDataTypeAsString(self):
        if self.dataType == INT:
            return "INT"
        elif self.dataType == FLOAT:
            return "FLOAT"
        elif self.dataType == FLOAT2:
            return "FLOAT2"
        elif self.dataType == FLOAT_VECTOR:
            return "FLOAT_VECTOR"
        elif self.dataType == FLOAT_COLOR:
            return "FLOAT_COLOR"
        elif self.dataType == BYTE_COLOR:
            return "BYTE_COLOR"
        return "BOOLEAN"

    def getDataType(self):
        if self.dataType == INT:
            return LongList
        elif self.dataType == FLOAT:
            return FloatList
        elif self.dataType == FLOAT2:
            return Vector2DList
        elif self.dataType == FLOAT_VECTOR:
            return Vector3DList
        elif self.dataType in [FLOAT_COLOR, BYTE_COLOR]:
            return ColorList
        return BooleanList
