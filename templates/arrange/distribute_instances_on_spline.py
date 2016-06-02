import bpy
from ... base_types.template import Template

class DistributeInstancesOnSplineTemplate(bpy.types.Operator, Template):
    bl_idname = "an.distribute_instances_on_spline_template"
    bl_label = "Distribute Instances on Spline"
    nodeOffset = (-500, 200)

    def insert(self):
        xDivisionsNode = self.newNode("an_DataInputNode", x = 0, y = 0, label = "X Divisons")
        xDivisionsNode.assignedType = "Integer"
        xDivisionsNode.inputs[0].value = 10

        instancerNode = self.newNode("an_ObjectInstancerNode", x = 220, y = 181)
        getSplineSamplesNode = self.newNode("an_GetSplineSamplesNode", x = 220, y = -39)
        invokeSubprogramNode = self.newNode("an_InvokeSubprogramNode", x = 530, y = 90)

        loopInputNode = self.newNode("an_LoopInputNode", x = 530, y = -150)
        loopInputNode.newIterator("Object List", name = "Object")
        loopInputNode.newIterator("Vector List", name = "Location")
        loopInputNode.newIterator("Vector List", name = "Direction")

        directionToRotationNode = self.newNode("an_DirectionToRotationNode", x = 800, y = -270)
        transformsOutputNode = self.newNode("an_ObjectTransformsOutputNode", x = 1050, y = -100)
        transformsOutputNode.useLocation = [True, True, True]
        transformsOutputNode.useRotation = [True, True, True]

        invokeSubprogramNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(xDivisionsNode.outputs[0], instancerNode.inputs[0])
        self.newLink(xDivisionsNode.outputs[0], getSplineSamplesNode.inputs[1])
        self.newLink(instancerNode.outputs[0], invokeSubprogramNode.inputs[0])
        self.newLink(getSplineSamplesNode.outputs[0], invokeSubprogramNode.inputs[1])
        self.newLink(getSplineSamplesNode.outputs[1], invokeSubprogramNode.inputs[2])

        self.newLink(loopInputNode.outputs[4], directionToRotationNode.inputs[0])
        self.newLink(loopInputNode.outputs[2], transformsOutputNode.inputs[0])
        self.newLink(loopInputNode.outputs[3], transformsOutputNode.inputs[1])
        self.newLink(directionToRotationNode.outputs[0], transformsOutputNode.inputs[2])
