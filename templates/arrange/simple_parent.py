import bpy
from ... base_types.template import Template

class SimpleParentTemplate(bpy.types.Operator, Template):
    bl_idname = "an.simple_parent_template"
    bl_label = "Simple Parent"
    nodeOffset = (-200, 100)

    def insert(self):
        matrixInputNode = self.newNode("an_ObjectMatrixInputNode", x = 0, y = 0)
        composeMatrixNode = self.newNode("an_ComposeMatrixNode", x = 0, y = -120)
        composeMatrixNode.inputs[0].value = [4, 0, 0]
        matrixMathNode = self.newNode("an_MatrixMathNode", x = 200, y = 0)
        matrixOutputNode = self.newNode("an_ObjectMatrixOutputNode", x = 400, y = 0)

        self.newLink(matrixMathNode.outputs[0], matrixOutputNode.inputs[1])
        self.newLink(matrixInputNode.outputs[0], matrixMathNode.inputs[0])
        self.newLink(composeMatrixNode.outputs[0], matrixMathNode.inputs[1])
