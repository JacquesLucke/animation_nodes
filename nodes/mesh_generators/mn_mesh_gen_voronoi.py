import bpy
from bpy.types import Node
import mathutils
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

from . import Surfaces

defaultOffsetEdgesMin = 0.1
defaultOffsetEdgesMax = 0.2

class mn_MeshGenerationVoronoiNode(Node, AnimationNode):
    bl_idname = "mn_MeshGenerationVoronoiNode"
    bl_label = "Generate Voronoi Diagram"
        
    def updateSocketVisibility(self):
        self.inputs["Offset Edges Min."].hide = not self.offsetEdges
        self.inputs["Offset Edges Max."].hide = not self.offsetEdges
    
    def modeChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()

    offsetEdges = bpy.props.BoolProperty(name = "Offset Edges", default = False, update = modeChanged)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "offsetEdges")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "World Locations")
        self.inputs.new("mn_FloatSocket", "Offset Edges Min.").number = defaultOffsetEdgesMin
        self.inputs.new("mn_FloatSocket", "Offset Edges Max.").number = defaultOffsetEdgesMax
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"World Locations" : "worldLocations",
                "Offset Edges Min." : "offsetEdgesMin",
                "Offset Edges Max." : "offsetEdgesMax"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, worldLocations, offsetEdgesMin, offsetEdgesMax):
        if len(worldLocations) < 3: return False
        
        if self.offsetEdges:
            if offsetEdgesMax < offsetEdgesMin: return False
            
        return True

    def execute(self, worldLocations, offsetEdgesMin, offsetEdgesMax):
        vertices = []
        polygons = []
        if not self.canExecute(worldLocations, offsetEdgesMin, offsetEdgesMax):
            return vertices, polygons

        if self.offsetEdges:
            if offsetEdgesMin < 0.0: offsetEdgesMin = 0.0
            if offsetEdgesMin > 1.0: offsetEdgesMin = 1.0
            if offsetEdgesMax < 0.0: offsetEdgesMax = 0.0
            if offsetEdgesMax > 1.0: offsetEdgesMax = 1.0
            
        try:
            xbuff, ybuff = 0, 0 # TODO: as inputs?
            voronoiSurface = Surfaces.VoronoiSurface(worldLocations, xbuff, ybuff)
            vertices, polygons = voronoiSurface.Calculate(self.offsetEdges, offsetEdgesMin, offsetEdgesMax)
        except: pass

        return vertices, polygons
