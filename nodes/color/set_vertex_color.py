import bpy, random
from ... base_types.node import AnimationNode
from ... events import propertyChanged


class SetVertexColor(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetVertexColor"
    bl_label = "Set Vertex Color"
    
    inputNames = { "Object" : "object",
                   "Color" : "color" }
    outputNames = { "Object" : "object" }                   
    
    enabled = bpy.props.BoolProperty(default = True, update = propertyChanged)
    vertexColorName = bpy.props.StringProperty(default = "Col", update = propertyChanged)
    checkIfColorIsSet = bpy.props.BoolProperty(default = True)
    
    def create(self):
        self.inputs.new("an_ObjectSocket", "Object")
        self.inputs.new("an_ColorSocket", "Color")
        self.outputs.new("an_ObjectSocket", "Object")
        
    def draw(self, layout):
        layout.prop(self, "enabled", text = "Enabled")
        layout.prop(self, "checkIfColorIsSet", text = "Check Color")

    def execute(self, object, color):
        if not self.enabled: return object
        if object is None: return object
        
        mesh = object.data
    
        colorLayer = mesh.vertex_colors.get(self.vertexColorName)
        if colorLayer is None:
            colorLayer = mesh.vertex_colors.new(self.vertexColorName)
        
        color = color[:3]
        if self.checkIfColorIsSet:
            oldColor = colorLayer.data[0].color
            if abs(color[0] * 100 + color[1] * 10 + color[2] - oldColor[0] * 100 - oldColor[1] * 10 - oldColor[2]) < 0.001:
                return object
        
        for meshColor in colorLayer.data:
            meshColor.color = color
        return object