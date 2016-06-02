import bpy
from ... base_types.node import AnimationNode

class FindNearestSurfacePointNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FindNearestSurfacePointNode"
    bl_label = "Find Nearest Surface Point"
    bl_width_default = 165

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")
        self.newInput("Vector", "Vector", "vector", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Max Distance", "maxDistance",
                      minValue = 0, value = 1e6, hide = True)

        self.newOutput("Vector", "Location", "location")
        self.newOutput("Vector", "Normal", "normal")
        self.newOutput("Float", "Distance", "distance")
        self.newOutput("Integer", "Polygon Index", "polygonIndex").hide = True
        self.newOutput("Boolean", "Hit", "hit")

    def getExecutionCode(self):
        yield "location, normal, polygonIndex, distance = bvhTree.find_nearest(vector, maxDistance)"
        yield "if location is None:"
        yield "    location = Vector((0, 0, 0))"
        yield "    normal = Vector((0, 0, 0))"
        yield "    polygonIndex = -1"
        yield "    distance = 0"
        yield "    hit = False"
        yield "else: hit = True"
