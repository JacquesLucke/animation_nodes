import bpy
from ... base_types import Template

class AnimateIndividualLettersTemplate(bpy.types.Operator, Template):
    bl_idname = "an.animate_individual_letters_template"
    bl_label = "Animate Individual Letters"
    nodeOffset = (-0, 0)

    def insert(self):
        separateTextNode = self.newNode("an_SeparateTextObjectNode", x = 0, y = 0)
        invokeNode = self.newNode("an_InvokeSubprogramNode", x = 250, y = 0)

        loopInputNode = self.newNode("an_LoopInputNode", x = 0, y = -250)
        loopInputNode.newIterator("Object List", name = "Object")
        loopInputNode.subprogramName = "Animate Objects"
        idKeyNode = self.newNode("an_ObjectIDKeyNode", x = 400, y = -420)
        idKeyNode.keyDataType = "Transforms"
        idKeyNode.keyName = "Initial Transforms"
        composeMatrixNode = self.newNode("an_ComposeMatrixNode", x = 230, y = -340)
        timeInfoNode = self.newNode("an_TimeInfoNode", x = 350, y = -220)
        animateNode = self.newNode("an_AnimateDataNode", x = 640, y = -300)
        animateNode.dataType = "Matrix"
        animateNode.inputs["Interpolation"].category = "BACK"
        objectMatrixOutput = self.newNode("an_ObjectMatrixOutputNode", x = 870, y = -190)

        invokeNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(separateTextNode.outputs[0], invokeNode.inputs[0])

        self.newLink(loopInputNode.outputs[2], idKeyNode.inputs[0])
        self.newLink(loopInputNode.outputs[2], objectMatrixOutput.inputs[0])
        self.newLink(timeInfoNode.outputs[0], animateNode.inputs[0])
        self.newLink(composeMatrixNode.outputs[0], animateNode.inputs[1])
        self.newLink(idKeyNode.outputs[4], animateNode.inputs[2])
        self.newLink(animateNode.outputs[1], objectMatrixOutput.inputs[1])
