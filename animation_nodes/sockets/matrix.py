import bpy
from bpy.props import *
from mathutils import Matrix
from .. data_structures import Matrix4x4List
from .. base_types import AnimationNodeSocket, CListSocket
from .. utils.nodes import newNodeAtCursor, invokeTranslation

class MatrixSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MatrixSocket"
    bl_label = "Matrix Socket"
    dataType = "Matrix"
    drawColor = (1, 0.56, 0.3, 1)
    storable = True
    comparable = False

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        if not self.is_linked:
            self.invokeFunction(row, node, "createComposeMatrixNode", icon = "PLUS")
        row.label(text = " " + text)

    def createComposeMatrixNode(self):
        node = newNodeAtCursor("an_ComposeMatrixNode")
        node.nodeTree.links.new(node.outputs[0], self)
        invokeTranslation()

    @classmethod
    def getDefaultValue(cls):
        return Matrix.Identity(4)

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Matrix):
            return value, 0
        else:
            try: return Matrix(value), 1
            except: return cls.getDefaultValue(), 2

class MatrixListSocket(bpy.types.NodeSocket, CListSocket):
    bl_idname = "an_MatrixListSocket"
    bl_label = "Matrix List Socket"
    dataType = "Matrix List"
    baseType = MatrixSocket
    drawColor = (1, 0.56, 0.3, 0.5)
    storable = True
    comparable = False
    listClass = Matrix4x4List
