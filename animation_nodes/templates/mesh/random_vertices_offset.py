import bpy
from ... base_types import Template

class RandomVerticesOffsetTemplate(bpy.types.Operator, Template):
    bl_idname = "an.random_vertices_offset_template"
    bl_label = "Random Vertices Offset"
    nodeOffset = (-500, 200)

    def insert(self):
        meshInputNode = self.newNode("an_ObjectMeshDataNode", x = 0, y = 0)
        invokeSubprogramNode = self.newNode("an_InvokeSubprogramNode", x = 210, y = 115)
        combineMeshDataNode = self.newNode("an_CombineMeshDataNode", x = 450, y = 30)
        meshOutput = self.newNode("an_MeshObjectOutputNode", x = 650, y = 81)
        meshOutput.meshDataType = "MESH_DATA"
        meshOutput.inputs["Mesh Data"].isUsed = True

        loopInputNode = self.newNode("an_LoopInputNode", x = 70, y = -240)
        loopInputNode.subprogramName = "Move Vertices"
        loopInputNode.newIterator("Vector List", name = "Vector")
        loopInputNode.newParameter("Float", name = "Strength", defaultValue = 0.3)

        randomVectorNode = self.newNode("an_RandomVectorNode", x = 310, y = -330)
        vectorMathNode = self.newNode("an_VectorMathNode", x = 515, y = -235)

        loopOutputNode = self.newNode("an_LoopGeneratorOutputNode", x = 720, y = -212)
        loopOutputNode.loopInputIdentifier = loopInputNode.identifier
        loopOutputNode.outputName = "Vector List"
        loopOutputNode.listDataType = "Vector List"
        loopOutputNode.useList = False

        invokeSubprogramNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(meshInputNode.outputs[0], invokeSubprogramNode.inputs[0])
        self.newLink(meshInputNode.outputs[1], combineMeshDataNode.inputs[1])
        self.newLink(meshInputNode.outputs[2], combineMeshDataNode.inputs[2])
        self.newLink(loopInputNode.outputs[2], vectorMathNode.inputs[0])
        self.newLink(randomVectorNode.outputs[0], vectorMathNode.inputs[1])
        self.newLink(vectorMathNode.outputs[0], loopOutputNode.inputs[0])
        self.newLink(loopInputNode.outputs[4], randomVectorNode.inputs[1])
        self.newLink(loopInputNode.outputs[0], randomVectorNode.inputs[0])
        self.newLink(invokeSubprogramNode.outputs[0], combineMeshDataNode.inputs[0])
        self.newLink(combineMeshDataNode.outputs[0], meshOutput.inputs[1])
