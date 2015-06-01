import bpy
from bpy.types import Node
import mathutils
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Surfaces

# utility properties & functions
defaultEquation = "x*y"
defaultStart = -1.0
defaultEnd = 1.0

class mn_MeshGenerationHeightFunctionNode(Node, AnimationNode):
    bl_idname = "mn_MeshGenerationHeightFunctionNode"
    bl_label = "Generate Height Function"
    
    coordinates_items = [ ("Cartesian", "Cartesian", "Uses an ordinary, orthonormal XY system"), 
                          ("Polar", "Polar", "Uses polar coordinates, ie, a radius R and an angle A")]
    coordinates = bpy.props.EnumProperty(name = "Coordinates", items = coordinates_items, default = "Cartesian")
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "coordinates")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Equation").string = defaultEquation
        self.inputs.new("mn_IntegerSocket", "Resolution X/R").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_IntegerSocket", "Resolution Y/A").number = Surfaces.defaultResolutionSynthesis
        self.inputs.new("mn_FloatSocket", "Start X/R").number = defaultStart
        self.inputs.new("mn_FloatSocket", "End X/R").number = defaultEnd
        self.inputs.new("mn_FloatSocket", "Start Y/A").number = defaultStart
        self.inputs.new("mn_FloatSocket", "End Y/A").number = defaultEnd
        self.outputs.new("mn_VectorListSocket", "Vertex World Locations")
        self.outputs.new("mn_PolygonIndicesListSocket", "Polygon Indices")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Equation" : "equation",
                "Resolution X/R" : "resXR",
                "Resolution Y/A" : "resYA",
                "Start X/R" : "startXR",
                "End X/R" : "endXR",
                "Start Y/A" : "startYA",
                "End Y/A" : "endYA"}

    def getOutputSocketNames(self):
        return {"Vertex World Locations" : "vertices",
                "Polygon Indices" : "polygons"}

    def canExecute(self, equation, resXR, resYA, startXR, endXR, startYA, endYA):
        try: self.expr_args = (compile(equation, __file__, 'eval'), {"__builtins__": None}, Surfaces.safe_dict)
        except: return False
        
        if resXR < 2: return False
        if resYA < 2: return False
        
        # if endXR <= startXR: return False
        # if endYA <= startYA: return False
            
        return True

    def execute(self, equation, resXR, resYA, startXR, endXR, startYA, endYA):
        vertices = []
        polygons = []
        if not self.canExecute(equation, resXR, resYA, startXR, endXR, startYA, endYA):
            print("### NOT mn_MeshGenerationHeightFunctionNode.canExecute()")
            return vertices, polygons

        try:
            if self.coordinates == "Cartesian":
                heightFunctionCartesianSurface = Surfaces.HeightFunctionCartesianSurface(equation, startXR, endXR, startYA, endYA)
                vertices, polygons = heightFunctionCartesianSurface.Calculate(resXR, resYA)
                return vertices, polygons
            if self.coordinates == "Polar":
                heightFunctionPolarSurface = Surfaces.HeightFunctionPolarSurface(equation, startXR, endXR, startYA, endYA)
                vertices, polygons = heightFunctionPolarSurface.Calculate(resXR, resYA)
        except: pass
            
        return vertices, polygons
        
        
class AssignPreset(bpy.types.Operator):
    bl_idname = "mn.assign_preset_mesh_gen_height_function"
    bl_label = "Assign"
    bl_description = "Assign the selected preset to the selected node"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()

    def invoke(self, context, event):
        node = getNode(self.nodeTreeName, self.nodeName)

        # TODO
        print("AssignPreset.invoke()")
            
        return {'FINISHED'}
    