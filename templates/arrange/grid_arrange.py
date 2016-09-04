import bpy
from bpy.props import *
from ... base_types import Template

class GridArrangeObjectsTemplate(bpy.types.Operator, Template):
    bl_idname = "an.grid_arrange_objects_template"
    bl_label = "Grid Arrange Objects"
    nodeOffset = (-500, 200)

    def insert(self):
        xDivisionsNode = self.newNode("an_DataInputNode", x = 0, y = 0, label = "X Divisions")
        xDivisionsNode.assignedType = "Integer"
        xDivisionsNode.inputs[0].value = 5

        yDivisionsNode = self.newNode("an_DataInputNode", x = 0, y = -140, label = "Y Divisions")
        yDivisionsNode.assignedType = "Integer"
        yDivisionsNode.inputs[0].value = 5

        gridMeshNode = self.newNode("an_GridMeshNode", x = 300, y = -100)
        calcAmountNode = self.newNode("an_FloatMathNode", x = 300, y = 100)
        objectInstancerNode = self.newNode("an_ObjectInstancerNode", x = 530, y = 100)

        invokeSubprogramNode = self.newNode("an_InvokeSubprogramNode", x = 750, y = -25)

        loopInputNode = self.newNode("an_LoopInputNode", x = 550, y = -260)
        loopInputNode.newIterator("Object List")
        loopInputNode.newIterator("Vector List")

        transformsOutputNode = self.newNode("an_ObjectTransformsOutputNode", x = 850, y = -215)
        transformsOutputNode.useLocation = [True] * 3

        invokeSubprogramNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(xDivisionsNode.outputs[0], gridMeshNode.inputs[0])
        self.newLink(yDivisionsNode.outputs[0], gridMeshNode.inputs[1])
        self.newLink(xDivisionsNode.outputs[0], calcAmountNode.inputs[0])
        self.newLink(yDivisionsNode.outputs[0], calcAmountNode.inputs[1])
        self.newLink(calcAmountNode.outputs[0], objectInstancerNode.inputs[0])
        self.newLink(objectInstancerNode.outputs[0], invokeSubprogramNode.inputs[0])
        self.newLink(gridMeshNode.outputs[0], invokeSubprogramNode.inputs[1])

        self.newLink(loopInputNode.outputs[2], transformsOutputNode.inputs[0])
        self.newLink(loopInputNode.outputs[3], transformsOutputNode.inputs[1])
