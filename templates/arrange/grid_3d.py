import bpy
from ... base_types.template import Template

class Grid3DTemplate(bpy.types.Operator, Template):
    bl_idname = "an.grid_3d_template"
    bl_label = "3D Grid"
    nodeOffset = (-500, 200)

    def insert(self):
        invokeGridLoopNode = self.newNode('an_InvokeSubprogramNode', x = 0, y = 0)
        getListLengthNode = self.newNode('an_GetListLengthNode', x = 250, y = -50)
        instancerNode = self.newNode('an_ObjectInstancerNode', x = 463, y = 47)
        invokeSetObjectsNode = self.newNode('an_InvokeSubprogramNode', x = 670, y = 75)

        gridLoopInputNode = self.newNode('an_LoopInputNode', x = 0, y = -250)
        gridLoopInputNode.subprogramName = "3D Grid Points"
        multiplyNode = self.newNode('an_FloatMathNode', x = 250, y = -250)
        combineVectorNode = self.newNode('an_CombineVectorNode', x = 450, y = -250)
        gridMeshNode = self.newNode('an_GridMeshNode', x = 660, y = -250)

        generatorOutputNode = self.newNode('an_LoopGeneratorOutputNode', x = 880, y = -250, label = 'Vector List')
        generatorOutputNode.loopInputIdentifier = gridLoopInputNode.identifier
        generatorOutputNode.outputName = 'Vector List'
        generatorOutputNode.listDataType = 'Vector List'
        generatorOutputNode.addType = 'EXTEND'

        setObjectsLoopInputNode = self.newNode('an_LoopInputNode', x = 0, y = -530)
        setObjectsLoopInputNode.subprogramName = "Set Object Positions"
        setObjectsLoopInputNode.newIterator('Object List', name = 'Object')
        setObjectsLoopInputNode.newIterator('Vector List', name = 'Vector')
        transformsOutputNode = self.newNode('an_ObjectTransformsOutputNode', x = 250, y = -530)
        transformsOutputNode.useLocation = [True, True, True]

        invokeGridLoopNode.subprogramIdentifier = gridLoopInputNode.identifier
        invokeSetObjectsNode.subprogramIdentifier = setObjectsLoopInputNode.identifier

        self.updateSubprograms()
        invokeGridLoopNode.inputs[0].value = 5

        self.newLink(gridLoopInputNode.outputs[0], multiplyNode.inputs[0])
        self.newLink(combineVectorNode.outputs[0], gridMeshNode.inputs[4])
        self.newLink(multiplyNode.outputs[0], combineVectorNode.inputs[2])
        self.newLink(gridMeshNode.outputs[0], generatorOutputNode.inputs[1])
        self.newLink(getListLengthNode.outputs[0], instancerNode.inputs[0])
        self.newLink(setObjectsLoopInputNode.outputs[2], transformsOutputNode.inputs[0])
        self.newLink(setObjectsLoopInputNode.outputs[3], transformsOutputNode.inputs[1])
        self.newLink(instancerNode.outputs[0], invokeSetObjectsNode.inputs[0])
        self.newLink(invokeGridLoopNode.outputs[0], invokeSetObjectsNode.inputs[1])
        self.newLink(invokeGridLoopNode.outputs[0], getListLengthNode.inputs[0])
