import bpy
from bpy.types import Node
import mathutils
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

from . import Surfaces
from . import DelaunayVoronoi

defaultBuffer = 0.0

class mn_MeshGenerationVoronoiDelaunayNode(Node, AnimationNode):
    bl_idname = "mn_MeshGenerationVoronoiDelaunayNode"
    bl_label = "Generate Voronoi/Delaunay"
        
    def updateSocketVisibility(self):
        self.inputs["Buffer X"].hide = not (self.mode == "Voronoi")
        self.inputs["Buffer Y"].hide = not (self.mode == "Voronoi")
    
    def modeChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    modes_items = [ ("Voronoi", "Voronoi", "Generates a (2D) (XY) Voronoi Diagram"), 
                    ("Delaunay", "Delaunay", "Generates a (2.5-D) (XY) Delaunay Triangulation")]
    mode = bpy.props.EnumProperty(name = "Mode", items = modes_items, default = "Voronoi", update = modeChanged)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "World Locations")
        self.inputs.new("mn_FloatSocket", "Buffer X").number = defaultBuffer
        self.inputs.new("mn_FloatSocket", "Buffer Y").number = defaultBuffer
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"World Locations" : "worldLocations",
                "Buffer X" : "bufferX",
                "Buffer Y" : "bufferY"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, worldLocations, bufferX, bufferY):
        if len(worldLocations) < 3: return False
            
        return True

    def execute(self, worldLocations, bufferX, bufferY):
        vertices = []
        polygons = []
        if not self.canExecute(worldLocations, bufferX, bufferY):
            return vertices, polygons

        try:
            if self.mode == "Voronoi":
                if bufferX < 0.0: bufferX = 0.0
                if bufferY < 0.0: bufferY = 0.0
                voronoiSurface = Surfaces.VoronoiSurface(worldLocations, bufferX, bufferY)
                vertices, polygons = voronoiSurface.Calculate()
                return vertices, polygons
            if self.mode == "Delaunay":
                polygons = DelaunayVoronoi.computeDelaunayTriangulation(worldLocations)
                return worldLocations, polygons
        except: pass

        return vertices, polygons
