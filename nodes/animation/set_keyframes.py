import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged
from ... mn_utils import *

pathTypes = ("Custom", "Location", "Rotation", "Scale", "LocRotScale")
pathTypeItems = [(pathType, pathType, "") for pathType in pathTypes]

class mn_KeyframePath(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(default = "", update = nodePropertyChanged, description = "Path to the property")
    index = bpy.props.IntProperty(default = -1, update = nodePropertyChanged, min = -1, soft_max = 2, description = "Used index if the path points to an array (-1 will set a keyframe on every index)")

class SetKeyframesNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SetKeyframesNode"
    bl_label = "Set Keyframes"
        
    paths = bpy.props.CollectionProperty(type = mn_KeyframePath)
    
    selectedPathType = bpy.props.EnumProperty(default = "Location", items = pathTypeItems, name = "Path Type")
    attributePath = bpy.props.StringProperty(default = "", name = "Attribute Path")
    
    def create(self):
        self.width = 200
        self.inputs.new("mn_BooleanSocket", "Enable").value = False
        self.inputs.new("mn_BooleanSocket", "Set Keyframe")
        self.inputs.new("mn_BooleanSocket", "Remove Unwanted")
        self.inputs.new("mn_ObjectSocket", "Object")
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        row.prop(self, "selectedPathType", text = "")
        new = row.operator("mn.new_property_to_list_node", text = "", icon = "PLUS")
        new.nodeTreeName = self.id_data.name
        new.nodeName = self.name
        
        col = layout.column(align = True)
        for i, item in enumerate(self.paths):
            row = col.row(align = True)
            split = row.split(align = True, percentage = 0.7)
            split.prop(item, "path", text = "")
            split.prop(item, "index", text = "")
            remove = row.operator("mn.remove_property_from_list_node", icon = "X", text = "")
            remove.nodeTreeName = self.id_data.name
            remove.nodeName = self.name
            remove.index = i
        
    def getInputSocketNames(self):
        return {"Enable" : "enable",
                "Set Keyframe" : "setKeyframe",
                "Remove Unwanted" : "removeUnwanted",
                "Object" : "object"}
                
    def getOutputSocketNames(self):
        return {}
        
    def execute(self, enable, setKeyframe, removeUnwanted, object):
        if not enable: return
        frame = getCurrentFrame()
        if setKeyframe:
            for item in self.paths:
                try:
                    obj, path = self.getResolvedNestedPath(object, item.path)
                    obj.keyframe_insert(data_path = path, frame = frame, index = item.index)
                except: pass
        elif removeUnwanted:
            for item in self.paths:
                try:
                    obj, path = self.getResolvedNestedPath(object, item.path)
                    obj.keyframe_delete(data_path = path, frame = frame, index = item.index)
                except: pass
                
    def getResolvedNestedPath(self, object, path):
        index = path.find(".")
        if index == -1: return object, path
        else:
            data = eval("object." + path[:index])
            return data, path[index+1:]
            
    def newPath(self, path, index = -1):
        item = self.paths.add()
        item.path = path
        item.index = index
        
    def addItemToList(self):
        type = self.selectedPathType
        if type == "Custom": self.newPath("")
        elif type == "Location": self.newPath("location")
        elif type == "Rotation": self.newPath("rotation_euler")
        elif type == "Scale": self.newPath("scale")
        elif type == "LocRotScale":
            self.newPath("location")
            self.newPath("rotation_euler")
            self.newPath("scale")
    
    def removeItemFromList(self, index):
        self.paths.remove(index)
        
        
