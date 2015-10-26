import bpy
from bpy.props import *
from ... base_types.template import Template
from ... utils.layout import writeText

connectionTypeItems = [
    ("EDGE", "Edge", ""),
    ("POLYGON", "Polygon", ""),
    ("SPLINE", "Spline", "") ]

performanceInfo = """
Rough Performance Comparison:
Edge: 3.5s
Polygon: 6.1s
Spline: 11s
"""

class NetworkFromParticlesTemplate(bpy.types.Operator, Template):
    bl_idname = "an.network_from_particles_template"
    bl_label = "Network from Particles"
    nodeOffset = (-500, 150)
    menuWidth = 200

    connectionType = EnumProperty(items = connectionTypeItems)

    def drawDialog(self, layout):
        layout.prop(self, "connectionType", expand = True)
        layout.separator()
        writeText(layout, performanceInfo)

    def insert(self):
        particlesFromObjectNode = self.newNode('an_ParticlesFromObjectNode', x = 0, y = 0)
        filterParticlesNode = self.newNode('an_FilterParticlesNode', x = 220, y = 0)
        particlesInfoNode = self.newNode('an_ParticleListInfoNode', x = 450, y = 0)

        findEdgesNode = self.newNode('an_FindCloseVerticesNode', x = 650, y = -90)
        findEdgesNode.inputs[4].value = 0.6

        self.newLink(particlesFromObjectNode.outputs[0], filterParticlesNode.inputs[0])
        self.newLink(filterParticlesNode.outputs[0], particlesInfoNode.inputs[0])
        self.newLink(particlesInfoNode.outputs[0], findEdgesNode.inputs[0])

        if self.connectionType == "EDGE":
            combineMeshNode = self.newNode('an_CombineMeshDataNode', x = 860, y = 30)
            setOnObjectNode = self.newNode('an_SetMeshDataOnObjectNode', x = 1080, y = 30)

            self.newLink(particlesInfoNode.outputs[0], combineMeshNode.inputs[0])
            self.newLink(findEdgesNode.outputs[0], combineMeshNode.inputs[1])
            self.newLink(combineMeshNode.outputs[0], setOnObjectNode.inputs[1])

        if self.connectionType == "POLYGON":
            edgesToPlanesNode = self.newNode('an_EdgesToPlanesNode', x = 870, y = 70)
            combineMeshNode = self.newNode('an_CombineMeshDataNode', x = 1100, y = 70)
            setOnObjectNode = self.newNode('an_SetMeshDataOnObjectNode', x = 1315, y = 70)

            self.newLink(particlesInfoNode.outputs[0], edgesToPlanesNode.inputs[0])
            self.newLink(findEdgesNode.outputs[0], edgesToPlanesNode.inputs[1])
            self.newLink(edgesToPlanesNode.outputs[0], combineMeshNode.inputs[0])
            self.newLink(combineMeshNode.outputs[0], setOnObjectNode.inputs[1])
            self.newLink(edgesToPlanesNode.outputs[1], combineMeshNode.inputs[2])

        if self.connectionType == "SPLINE":
            splinesFromEdgesNode = self.newNode('an_SplinesFromEdgesNode', x = 870, y = 30)
            setOnObjectNode = self.newNode('an_SetSplinesOnObjectNode', x = 1080, y = 30)
            curveOutputNode = self.newNode('an_CurveObjectOutputNode', x = 1330, y = 30)
            curveOutputNode.inputs["Bevel Depth"].value = 0.005
            curveOutputNode.inputs["Bevel Depth"].isUsed = True

            self.newLink(particlesInfoNode.outputs[0], splinesFromEdgesNode.inputs[0])
            self.newLink(findEdgesNode.outputs[0], splinesFromEdgesNode.inputs[1])
            self.newLink(splinesFromEdgesNode.outputs[0], setOnObjectNode.inputs[1])
            self.newLink(setOnObjectNode.outputs[0], curveOutputNode.inputs[0])
