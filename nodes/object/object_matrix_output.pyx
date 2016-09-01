import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... utils.handlers import validCallback
from ... base_types.node import AnimationNode
from ... data_structures cimport Matrix4x4List
from ... math cimport toPyMatrix4

outputItems = [	("BASIS", "Basis", "", "NONE", 0),
                ("LOCAL", "Local", "", "NONE", 1),
                ("PARENT INVERSE", "Parent Inverse", "", "NONE", 2),
                ("WORLD", "World", "", "NONE", 3) ]

class ObjectMatrixOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixOutputNode"
    bl_label = "Object Matrix Output"

    @validCallback
    def useListChanged(self, context):
        self.recreateSockets()

    outputType = EnumProperty(items = outputItems, update = executionCodeChanged, default = "WORLD")
    useList = BoolProperty(name = "Use List", update = useListChanged, default = False)

    def create(self):
        self.recreateSockets()

    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        if self.useList:
            self.newInput("Object List", "Object List", "objects")
            self.newInput("Matrix List", "Matrix List", "matrices")
            self.newOutput("Object List", "Object List", "objects")
        else:
            self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
            self.newInput("Matrix", "Matrix", "matrix")
            self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "outputType", text = "")
        row.prop(self, "useList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionFunctionName(self):
        if self.useList:
            return "execute_List"
        else:
            return "execute_Single"

    def execute_Single(self, object, matrix):
        if object is not None:
            setattr(object, self.outputType, matrix)

    def execute_List(self, list objects, Matrix4x4List matrices):
        cdef size_t i
        cdef str attribute = self.outputType
        cdef size_t amount = min(len(objects), len(matrices))
        if attribute == "WORLD":
            for i in range(amount):
                obj = objects[i]
                if obj is not None:
                    obj.matrix_world = toPyMatrix4(matrices.data + i)
        elif attribute == "LOCAL":
            for i in range(amount):
                obj = objects[i]
                if obj is not None:
                    obj.matrix_local = toPyMatrix4(matrices.data + i)
        elif attribute == "PARENT INVERSE":
            for i in range(amount):
                obj = objects[i]
                if obj is not None:
                    obj.matrix_parent_inverse = toPyMatrix4(matrices.data + i)
        elif attribute == "BASIS":
            for i in range(amount):
                obj = objects[i]
                if obj is not None:
                    obj.matrix_basis = toPyMatrix4(matrices.data + i)
        return objects

    def getBakeCode(self):
        if self.useList:
            yield "for object in objects:"
            yield "    if object is not None:"
            yield "        object.keyframe_insert('location')"
            yield "        object.keyframe_insert('rotation_euler')"
            yield "        object.keyframe_insert('scale')"
        else:
            yield "if object is not None:"
            yield "    object.keyframe_insert('location')"
            yield "    object.keyframe_insert('rotation_euler')"
            yield "    object.keyframe_insert('scale')"
