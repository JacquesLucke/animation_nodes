import bpy, random
from ... utils.mn_math_utils import perlinNoise
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_SetVertexColor(Node, AnimationNode):
    bl_idname = "mn_SetVertexColor"
    bl_label = "Set Vertex Color"
    
    enabled = bpy.props.BoolProperty(default = True, update = nodePropertyChanged)
    vertexColorName = bpy.props.StringProperty(default = "Col", update = nodePropertyChanged)
    checkIfColorIsSet = bpy.props.BoolProperty(default = True)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object")
        self.inputs.new("mn_ColorSocket", "Color")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "enabled", text = "Enabled")
        layout.prop(self, "checkIfColorIsSet", text = "Check Color")
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Color" : "color"}
    def getOutputSocketNames(self):
        return {}

    def execute(self, object, color):
        if not self.enabled: return None
        if object is None: return None
        
        mesh = object.data
    
        colorLayer = mesh.vertex_colors.get(self.vertexColorName)
        if colorLayer is None:
            colorLayer = mesh.vertex_colors.new(self.vertexColorName)
        
        color = color[:3]
        if self.checkIfColorIsSet:
            oldColor = colorLayer.data[0].color
            if abs(color[0] * 100 + color[1] * 10 + color[2] - oldColor[0] * 100 - oldColor[1] * 10 - oldColor[2]) < 0.001:
                return None
        
        for meshColor in colorLayer.data:
            meshColor.color = color
        return None
        

