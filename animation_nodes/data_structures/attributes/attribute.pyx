from .. lists.clist cimport CList
from .. lists.base_lists cimport (
    LongList,
    FloatList,
    ColorList,
    BooleanList,
    Vector2DList,
    Vector3DList,
)

cListFromDataType = {
    INT: LongList,
    FLOAT: FloatList,
    FLOAT2: Vector2DList,
    FLOAT_VECTOR: Vector3DList,
    FLOAT_COLOR: ColorList,
    BYTE_COLOR: ColorList,
    BOOLEAN: BooleanList,
}

stringFromType = {
    UV_MAP: "UV_MAP",
    MATERIAL_INDEX: "MATERIAL_INDEX",
    VERTEX_COLOR: "VERTEX_COLOR",
    CUSTOM: "CUSTOM",
}

stringFromDomain = {
    POINT: "POINT",
    EDGE: "EDGE",
    FACE: "FACE",
    CORNER: "CORNER",
}

stringFromDataType = {
    INT: "INT",
    FLOAT: "FLOAT",
    FLOAT2: "FLOAT2",
    FLOAT_VECTOR: "FLOAT_VECTOR",
    FLOAT_COLOR: "FLOAT_COLOR",
    BYTE_COLOR: "BYTE_COLOR",
    BOOLEAN: "BOOLEAN",
}

cdef class Attribute:
    def __cinit__(self, str name,
                        AttributeType type,
                        AttributeDomain domain,
                        AttributeDataType dataType,
                        CList data):

        self.name = name
        self.type = type
        self.domain = domain
        self.dataType = dataType
        self.data = data

    def similar(self, Attribute other):
        return all((
            self.name == other.name,
            self.type == other.type,
            self.domain == other.domain,
            self.dataType == other.dataType
        ))

    def copy(self):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.copy())

    def replicate(self, Py_ssize_t amount):
        return Attribute(self.name, self.type, self.domain, self.dataType,
                         self.data.repeated(amount = amount))

    def append(self, Attribute source):
        self.data.extend(source.data)

    def appendZeros(self, int length):
        extension = self.getListType()(length = length)
        extension.fill(0)
        self.data.extend(extension)

    def prependZeros(self, int length):
        extension = self.getListType()(length = length)
        extension.fill(0)
        self.data = extension + self.data

    def getTypeAsString(self):
        return stringFromType(self.type)

    def getDomainAsString(self):
        return stringFromDomain(self.domain)

    def getListTypeAsString(self):
        return stringFromDataType(self.dataType)

    def getListType(self):
        return cListFromDataType.get(self.dataType)
