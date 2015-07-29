import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SetListElementNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SetListElementNode"
    bl_label = "Set Element"
    
    clampIndex = bpy.props.BoolProperty(default = True)
    
    def setSocketTypes(self, context):
        self.setSocketType(self.listTypesProperty)
        nodePropertyChanged(self, context)
    
    listTypes = [
        ("FLOAT", "Float", ""),
        ("STRING", "String", ""),
        ("OBJECT", "Object", "") ]
    listTypesProperty = bpy.props.EnumProperty(name = "Type", items = listTypes, default = "OBJECT", update = setSocketTypes)
    
    def init(self, context):
        forbidCompiling()
        self.setSocketType(self.listTypesProperty)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "listTypesProperty")
        layout.prop(self, "clampIndex", text = "Clamp Index")
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Value" : "value",
                "Index" : "index"}

    def getOutputSocketNames(self):
        return {"List" : "list"}
        
    def execute(self, list, value, index):
        if 0 <= index < len(list):
            list[index] = value
        return list
        
    def setSocketType(self, type):
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        if type == "FLOAT":
            self.inputs.new("mn_FloatListSocket", "List")
            self.inputs.new("mn_FloatSocket", "Value")
            self.inputs.new("mn_IntegerSocket", "Index")
            self.outputs.new("mn_FloatListSocket", "List")
        elif type == "STRING":
            self.inputs.new("mn_StringListSocket", "List")
            self.inputs.new("mn_StringSocket", "Value")
            self.inputs.new("mn_IntegerSocket", "Index")
            self.outputs.new("mn_StringSocket", "List")
        elif type == "OBJECT":
            self.inputs.new("mn_ObjectListSocket", "List")
            self.inputs.new("mn_ObjectSocket", "Value")
            self.inputs.new("mn_IntegerSocket", "Index")
            self.outputs.new("mn_ObjectListSocket", "List")
        allowCompiling()

