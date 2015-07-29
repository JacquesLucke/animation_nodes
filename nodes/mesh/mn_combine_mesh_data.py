import bpy, time
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *
from ... mn_cache import *

sourceTypeItems = [
    ("MESH_DATA", "Vertices and Indices", ""),
    ("POLYGONS", "Polygons", "") ]

class mn_CombineMeshData(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CombineMeshData"
    bl_label = "Combine Mesh Data"
    
    def sourceTypeChanged(self, context):
        self.updateHideStatus()
        nodePropertyChanged(self, context)
    
    sourceType = bpy.props.EnumProperty(items = sourceTypeItems, default = "MESH_DATA", name = "Source Type", update = sourceTypeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "Vertex Locations")
        self.inputs.new("mn_EdgeIndicesListSocket", "Edges Indices")
        self.inputs.new("mn_PolygonIndicesListSocket", "Polygons Indices")
        self.inputs.new("mn_PolygonListSocket", "Polygons")
        self.updateHideStatus()
        self.outputs.new("mn_MeshDataSocket", "Mesh Data")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "sourceType")
        
    def getInputSocketNames(self):
        return {"Vertex Locations" : "vertexLocations",
                "Edges Indices" : "edgesIndices",
                "Polygons Indices" : "polygonsIndices",
                "Polygons" : "polygons"}
                
    def getOutputSocketNames(self):
        return {"Mesh Data" : "meshData"}
    
        
    def execute(self, vertexLocations, edgesIndices, polygonsIndices, polygons):
        if self.sourceType == "MESH_DATA":
            meshData = MeshData(vertexLocations, edgesIndices, polygonsIndices)
        elif self.sourceType == "POLYGONS":
            meshData = getMeshDataFromPolygons(polygons)
            
        return meshData
        
    def updateHideStatus(self):
        self.inputs["Vertex Locations"].hide = True
        self.inputs["Edges Indices"].hide = True
        self.inputs["Polygons Indices"].hide = True
        self.inputs["Polygons"].hide = True
        
        if self.sourceType == "MESH_DATA":
            self.inputs["Vertex Locations"].hide = False
            self.inputs["Edges Indices"].hide = False
            self.inputs["Polygons Indices"].hide = False
        elif self.sourceType == "POLYGONS":
            self.inputs["Polygons"].hide = False

        
def getMeshDataFromPolygons(polygons):
    vertices = []
    polygonsIndices = []
    
    index = 0
    for polygon in polygons:
        vertices.extend([v.location for v in polygon.vertices])
        vertexAmount = len(polygon.vertices)
        polygonsIndices.append(tuple(range(index, index + vertexAmount)))
        index += vertexAmount
        
    return MeshData(vertices, [], polygonsIndices)