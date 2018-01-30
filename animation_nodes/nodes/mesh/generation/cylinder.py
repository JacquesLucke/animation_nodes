import bpy
from .... base_types import AnimationNode

class CylinderMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CylinderMeshNode"
    bl_label = "Cylinder Mesh"

    def create(self):
        self.newInput("Float", "Radius", "radius", value = 1, minValue = 0)
        self.newInput("Float", "Height", "height", value = 2, minValue = 0)
        self.newInput("Integer", "Resolution", "resolution", value = 8, minValue = 2)
        self.newInput("Boolean", "Caps", "caps", value = True)

        self.newOutput("Mesh", "Mesh", "mesh")
        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")

    def getExecutionCode(self, required):
        yield "cylinder = animation_nodes.algorithms.mesh_generation.cylinder"

        yield "_resolution = max(resolution, 2)"
        yield "_radius = max(radius, 0)"
        yield "_height = max(height, 0)"

        if "mesh" in required:
            yield "mesh = cylinder.getCylinderMesh(_radius, _height, _resolution, caps)"
            if "vertices" in required:
                yield "vertices = mesh.vertices.copy()"
            if "edgeIndices" in required:
                yield "edgeIndices = mesh.edges.copy()"
            if "polygonIndices" in required:
                yield "edgeIndices = mesh.polygons.copy()"
        else:
            if "vertices" in required:
                yield "vertices = cylinder.vertices(_radius, _radius, _resolution)"
            if "edgeIndices" in required:
                yield "edgeIndices = cylinder.edges(_resolution)"
            if "polygonIndices" in required:
                yield "polygonIndices = cylinder.polygons(_resolution, caps)"
