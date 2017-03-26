import bpy
from bpy.props import *
from ... math cimport Vector3, setVector3
from ... base_types import VectorizedNode
from ... data_structures cimport FalloffEvaluator, Vector3DList

class OffsetVectorsNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_OffsetVectorsNode"
    bl_label = "Offset Vectors"

    useOffsetList = VectorizedNode.newVectorizeProperty()

    errorMessage = StringProperty()
    clampFalloff = BoolProperty(name = "Clamp Falloff", default = False)

    def create(self):
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")

        self.newVectorizedInput("Vector", "useOffsetList",
            ("Offset", "offset", dict(value = (0, 0, 1))),
            ("Offset List", "offsets"))

        self.newOutput("Vector List", "Vector List", "vectors")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionFunctionName(self):
        if self.useOffsetList:
            return "execute_OffsetList"
        else:
            return "execute_SameOffset"

    def execute_OffsetList(self, Vector3DList vectors, falloff, Vector3DList offsets):
        cdef:
            FalloffEvaluator evaluator
            Vector3* _vectors = vectors.data
            Vector3* _offsets = offsets.data
            double influence
            long i

        self.errorMessage = ""
        if len(vectors) != len(offsets):
            self.errorMessage = "Vector lists have different lengths"
            return vectors
        try: evaluator = self.getFalloffEvaluator(falloff)
        except:
            self.errorMessage = "Falloff cannot be evaluated for vectors"
            return vectors

        for i in range(len(vectors)):
            influence = evaluator.evaluate(_vectors + i, i)
            _vectors[i].x += _offsets[i].x * influence
            _vectors[i].y += _offsets[i].y * influence
            _vectors[i].z += _offsets[i].z * influence

        return vectors

    def execute_SameOffset(self, Vector3DList vectors, falloff, offset):
        cdef:
            FalloffEvaluator evaluator
            Vector3* _vectors = vectors.data
            Vector3 _offset
            double influence
            long i

        self.errorMessage = ""
        try: evaluator = self.getFalloffEvaluator(falloff)
        except:
            self.errorMessage = "Falloff cannot be evaluated for vectors"
            return vectors

        setVector3(&_offset, offset)

        for i in range(vectors.length):
            influence = evaluator.evaluate(_vectors + i, i)
            _vectors[i].x += _offset.x * influence
            _vectors[i].y += _offset.y * influence
            _vectors[i].z += _offset.z * influence

        return vectors

    def getFalloffEvaluator(self, falloff):
        return falloff.getEvaluator("Location", self.clampFalloff)
