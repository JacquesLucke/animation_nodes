from .. lists.clist cimport CList
from .. lists.base_lists cimport (
    LongList,
    FloatList,
    ColorList,
    BooleanList,
    Vector2DList,
    Vector3DList,
)

cListFromDataType = {INT: LongList, FLOAT: FloatList, FLOAT2: Vector2DList,
                     FLOAT_VECTOR: Vector3DList, FLOAT_COLOR: ColorList,
                     BYTE_COLOR: ColorList, BOOLEAN: BooleanList}

cdef class Attribute:
    def __cinit__(self, str name = None,
                        AttributeType type = CUSTOM,
                        AttributeDomain domain = POINT,
                        AttributeDataType dataType = FLOAT,
                        CList data = None):

        self.name = name
        self.type = type
        self.domain = domain
        self.dataType = dataType
        self.data = data

    def copy(self):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.copy())

    def extend(self, data):
        self.data.extend(data)

    def replicate(self, Py_ssize_t amount):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.repeated(amount = amount))

    def appendAttribute(self, sourceAttribute = None, Py_ssize_t amount = -1):
        if sourceAttribute is not None:
            self.extend(sourceAttribute.data)
        else:
            extension = self.getListType()(length = amount)
            extension.fill(0)
            self.extend(extension)

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
        elif self.domain == FACE:
            return "FACE"
        return "CORNER"

    def getListTypeAsString(self):
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

    def getListType(self):
        return cListFromDataType.get(self.dataType)
