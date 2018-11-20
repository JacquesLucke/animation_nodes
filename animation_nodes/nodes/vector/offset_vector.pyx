import bpy
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... utils.clamp cimport clampLong
from ... math cimport Vector3, toVector3
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures cimport Falloff, FalloffEvaluator, Vector3DList, VirtualVector3DList, FloatList

specifiedStateItems = [
    ("START", "Start", "Given vector(s) set the start state", "NONE", 0),
    ("END", "End", "Given vector(s) set the end state", "NONE", 1)
]

class OffsetVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetVectorNode"
    bl_label = "Offset Vector"
    onlySearchTags = True
    errorHandlingType = "EXCEPTION"
    searchTags = [("Offset Vectors", {"useVectorList" : repr(True)})]

    __annotations__ = {}

    __annotations__["useVectorList"] = BoolProperty(name = "Use Vector List", default = False,
        update = AnimationNode.refresh)
    __annotations__["useOffsetList"] = VectorizedSocket.newProperty()

    __annotations__["specifiedState"] = EnumProperty(name = "Specified State", default = "START",
        description = "Specify wether the given vector(s) are the start or end state",
        items = specifiedStateItems, update = propertyChanged)

    __annotations__["clampFalloff"] = BoolProperty(name = "Clamp Falloff", default = False)

    def create(self):
        if self.useVectorList:
            self.newInput("Vector List", "Vectors", "inVectors", dataIsModified = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput(VectorizedSocket("Vector", "useOffsetList",
                ("Offset", "offset", dict(value = (0, 0, 1))),
                ("Offset List", "offsets")))
            self.newOutput("Vector List", "Vectors", "outVectors")
        else:
            self.newInput("Vector", "Vector", "inVector", dataIsModified = True)
            self.newInput("Falloff", "Falloff", "falloff")
            self.newInput("Vector", "Offset", "offset", value = (0, 0, 1))
            self.newInput("Integer", "Index", "index")
            self.newOutput("Vector", "Vector", "outVector")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "specifiedState", expand = True)
        row.prop(self, "useVectorList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionFunctionName(self):
        if self.useVectorList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_Single(self, vector, Falloff falloff, offset, index):
        cdef FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
        cdef float influence = evaluator(vector, index)

        if self.specifiedState == "END":
            influence = <float>1 - influence

        vector[0] += offset[0] * influence
        vector[1] += offset[1] * influence
        vector[2] += offset[2] * influence
        return vector

    def execute_List(self, Vector3DList vectors, falloff, offset):
        evaluator = self.getFalloffEvaluator(falloff)
        _offsets = VirtualVector3DList.create(offset, (0, 0, 0))
        offsetVector3DList(vectors, _offsets, evaluator, self.specifiedState == "END")
        return vectors

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("Location", self.clampFalloff)
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")


def offsetVector3DList(Vector3DList vectors, VirtualVector3DList offsets, FalloffEvaluator falloffEvaluator, bint invert = False):
    cdef FloatList influences = falloffEvaluator.evaluateList(vectors)

    cdef Vector3 *offset
    cdef float influence
    cdef Py_ssize_t i

    for i in range(len(vectors)):
        influence = influences.data[i]

        if invert:
            influence = <float>1 - influence

        offset = offsets.get(i)
        vectors.data[i].x += offset.x * influence
        vectors.data[i].y += offset.y * influence
        vectors.data[i].z += offset.z * influence
