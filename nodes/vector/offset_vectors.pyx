import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... math cimport Vector3, toVector3
from ... utils.handlers import validCallback
from ... base_types.node import AnimationNode
from ... data_structures cimport createFalloffEvaluator, FalloffEvaluator, Vector3DList

class OffsetVectorsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetVectorsNode"
    bl_label = "Offset Vectors"

    @validCallback
    def useOffsetListChanged(self, context):
        self.recreateInputs()

    useOffsetList = BoolProperty(name = "Use Offset List", default = False,
        update = useOffsetListChanged)

    errorMessage = StringProperty()
    clampFalloff = BoolProperty(name = "Clamp Falloff", default = False)

    def create(self):
        self.recreateInputs()
        self.newOutput("Vector List", "Vector List", "vectors")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        self.newInput("Vector List", "Vector List", "vectors", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        if self.useOffsetList:
            self.newInput("Vector List", "Offset List", "offsets")
        else:
            self.newInput("Vector", "Offset", "offset", value = (0, 0, 1))

    def draw(self, layout):
        layout.prop(self, "clampFalloff")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "useOffsetList")

    def getExecutionFunctionName(self):
        if self.useOffsetList:
            return "execute_OffsetList"
        else:
            return "execute_SameOffset"

    def execute_OffsetList(self, Vector3DList vectors, falloff, Vector3DList offsets):
        cdef:
            FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
            Vector3* _vectors = <Vector3*>vectors.base.data
            Vector3* _offsets = <Vector3*>offsets.base.data
            double influence
            long i

        self.errorMessage = ""
        if len(vectors) != len(offsets):
            self.errorMessage = "Vector lists have different lengths"
            return vectors
        if evaluator is None:
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
            FalloffEvaluator evaluator = self.getFalloffEvaluator(falloff)
            Vector3* _vectors = <Vector3*>vectors.base.data
            Vector3 _offset
            double influence
            long i

        self.errorMessage = ""
        if evaluator is None:
            self.errorMessage = "Falloff cannot be evaluated for vectors"
            return vectors

        toVector3(&_offset, offset)

        for i in range(vectors.getLength()):
            influence = evaluator.evaluate(_vectors + i, i)
            _vectors[i].x += _offset.x * influence
            _vectors[i].y += _offset.y * influence
            _vectors[i].z += _offset.z * influence

        return vectors

    def getFalloffEvaluator(self, falloff):
        return createFalloffEvaluator(falloff, "Location", self.clampFalloff)
