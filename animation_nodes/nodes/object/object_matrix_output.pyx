import bpy
from bpy.props import *
from ... math cimport toPyMatrix4
from ... sockets.info import isList
from ... events import executionCodeChanged
from ... data_structures cimport Matrix4x4List
from ... base_types import AnimationNode, VectorizedSocket

outputItems = [	("BASIS", "Basis", "", "NONE", 0),
                ("LOCAL", "Local", "", "NONE", 1),
                ("PARENT_INVERSE", "Parent Inverse", "", "NONE", 2),
                ("WORLD", "World", "", "NONE", 3) ]


class ObjectMatrixOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMatrixOutputNode"
    bl_label = "Object Matrix Output"

    outputType = EnumProperty(name = "Type", default = "WORLD",
        items = outputItems, update = executionCodeChanged)

    useObjectList = VectorizedSocket.newProperty()
    useMatrixList = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects")))

        self.newInput(VectorizedSocket("Matrix", ["useMatrixList", "useObjectList"],
            ("Matrix", "matrix"), ("Matrices", "matrices")))

        self.newOutput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object"), ("Objects", "objects")))

    def drawAdvanced(self, layout):
        layout.prop(self, "outputType", text = "Type")
        if self.outputType != "WORLD":
            layout.label("This mode might not work as expected", icon = "INFO")

    def getExecutionFunctionName(self):
        if isList(self.inputs[1].dataType):
            return "execute_List"
        return None

    def getExecutionCode(self, required):
        indent = ""
        if isList(self.inputs[0].dataType):
            yield "for object in objects:"
            indent = "    "

        t = self.outputType
        yield indent + "if object is not None:"
        if t == "BASIS":          yield indent + "    object.matrix_basis = matrix"
        if t == "LOCAL":          yield indent + "    object.matrix_local = matrix"
        if t == "PARENT_INVERSE": yield indent + "    object.matrix_parent_inverse = matrix"
        if t == "WORLD":          yield indent + "    object.matrix_world = matrix"

    def execute_List(self, list objects, Matrix4x4List matrices):
        cdef:
            Py_ssize_t i
            str attribute = self.outputType
            Py_ssize_t amount = min(len(objects), len(matrices))
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
        elif attribute == "PARENT_INVERSE":
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
        if self.useObjectList:
            yield "for object in objects:"
            yield "    if object is None: continue"
        else:
            yield "if object is not None:"
        yield "    object.keyframe_insert('location')"
        yield "    object.keyframe_insert('rotation_euler')"
        yield "    object.keyframe_insert('scale')"
