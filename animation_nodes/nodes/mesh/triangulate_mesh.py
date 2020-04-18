import bpy
from bpy.props import *
from ... data_structures import Mesh
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures.meshes.validate import createValidEdgesList

class TriangulateMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TriangulateMeshNode"
    bl_label = "Triangulate Mesh"
    errorHandlingType = "EXCEPTION"

    skipValidation: BoolProperty(name = "Skip Validation", default = False,
        description = "Skipping validation might cause Blender to crash when the data is not valid",
        update = propertyChanged)

    methodType: BoolProperty(name = "Use advanced method for Mesh Triangulation", default = False,
                             update = propertyChanged)

    def create(self):
        self.newInput("Mesh", "Mesh", "mesh", dataIsModified = True)

        self.newOutput("Mesh", "Mesh", "meshOut")

    def draw(self, layout):
        if self.skipValidation:
            layout.label(text = "Validation skipped", icon = "INFO")

    def drawAdvanced(self, layout):
        layout.prop(self, "skipValidation")
        layout.prop(self, "methodType", text = "Use advanced method for Mesh Triangulation")

    def execute(self, mesh):
        vertices = mesh.vertices
        if self.methodType: polygons = mesh.getTrianglePolygons(method = "EAR")
        else: polygons = mesh.getTrianglePolygons(method = "FAN")
        edges = createValidEdgesList(polygons = polygons)
        try:
            return Mesh(vertices, edges, polygons, skipValidation = self.skipValidation)
        except Exception as e:
            self.raiseErrorMessage(str(e))
