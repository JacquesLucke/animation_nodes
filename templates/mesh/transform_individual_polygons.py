import bpy
from ... base_types.template import Template

class TransformIndividualPolygonsTemplate(bpy.types.Operator, Template):
    bl_idname = "an.transform_individual_polygons_template"
    bl_label = "Transform Individual Polygons"
    nodeOffset = (-300, 400)

    def insert(self):
        meshDataNode = self.newNode('an_ObjectMeshDataNode', x = 0, y = 0)
        loopInvokeNode = self.newNode('an_InvokeSubprogramNode', x = 210, y = 0)
        meshFromPolygonsNode = self.newNode('an_MeshDataFromPolygonsNode', x = 450, y = 0)
        setOnObjectNode = self.newNode('an_SetMeshDataOnObjectNode', x = 660, y = 0)

        loopInputNode = self.newNode('an_LoopInputNode', x = 0, y = -300)
        loopInputNode.newIterator('Polygon List', name = 'Polygon')
        composeMatrixNode = self.newNode('an_ComposeMatrixNode', x = 280, y = -430)

        transformPolygon = self.newNode('an_TransformPolygonNode', x = 550, y = -295)

        generatorOutputNode = self.newNode('an_LoopGeneratorOutputNode', x = 760, y = -295, label = 'Transformed Polygons')
        generatorOutputNode.loopInputIdentifier = loopInputNode.identifier
        generatorOutputNode.outputName = 'Transformed Polygons'
        generatorOutputNode.listDataType = 'Polygon List'
        generatorOutputNode.addType = 'APPEND'

        loopInvokeNode.subprogramIdentifier = loopInputNode.identifier
        self.updateSubprograms()

        self.newLink(loopInputNode.outputs[2], transformPolygon.inputs[0])
        self.newLink(transformPolygon.outputs[0], generatorOutputNode.inputs[1])
        self.newLink(meshDataNode.outputs[3], loopInvokeNode.inputs[0])
        self.newLink(loopInvokeNode.outputs[0], meshFromPolygonsNode.inputs[0])
        self.newLink(meshFromPolygonsNode.outputs[0], setOnObjectNode.inputs[1])
        self.newLink(composeMatrixNode.outputs[0], transformPolygon.inputs[1])
