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

    @property
    def typeAsString(self):
        if self.type == UVMAP:
            return "UVMAP"
        elif self.type == MATERIAL_INDEX:
            return "MATERIAL_INDEX"
        elif self.type == VERTEX_COLOR:
            return "VERTEX_COLOR"
        return "CUSTOM"

    @typeAsString.setter
    def typeAsString(self, type):
        if type == "UVMAP":
            self.type = UVMAP
        elif type == "MATERIAL_INDEX":
            self.type = MATERIAL_INDEX
        elif type == "VERTEX_COLOR":
            self.type = VERTEX_COLOR
        else:
            self.type = CUSTOM

    @property
    def domainAsString(self):
        if self.domain == POINT:
            return "POINT"
        elif self.domain == EDGE:
            return "EDGE"
        elif self.domain == POLYGON:
            return "POLYGON"
        return "CORNER"

    @domainAsString.setter
    def domainAsString(self, domain):
        if domain == "POINT":
            self.domain = POINT
        elif domain == "EDGE":
            self.domain = EDGE
        elif domain == "POLYGON":
            self.domain = POLYGON
        else:
            self.domain = CORNER

    @property
    def dataTypeAsString(self):
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

    @dataTypeAsString.setter
    def dataTypeAsString(self, dataType):
        if dataType == "INT":
            self.dataType = INT
        elif dataType == "FLOAT":
            self.dataType = FLOAT
        elif dataType == "FLOAT2":
            self.dataType = FLOAT2
        elif dataType == "FLOAT_VECTOR":
            self.dataType = FLOAT_VECTOR
        elif dataType == "FLOAT_COLOR":
            self.dataType = FLOAT_COLOR
        elif dataType == "BYTE_COLOR":
            self.dataType = BYTE_COLOR
        else:
            self.dataType = BOOLEAN

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
