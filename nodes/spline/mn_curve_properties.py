import bpy
from bpy.types import Node
from bpy.props import *
from ... utils.mn_node_utils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... sockets.mn_socket_info import getIdNameFromDataType

possibleProperties = {
    "bevel_depth" : ("Bevel Depth", "Float", 0),
    "bevel_resolution" : ("Bevel Resolution", "Integer", 0),
    "offset" : ("Offset", "Float", 0),
    "extrude" : ("Extrude", "Float", 0),
    "taper_object" : ("Taper Object", "Object", ""),
    "bevel_object" : ("Bevel Object", "Object", ""),
    "resolution_u" : ("Preview Resolution", "Integer", 12),
    "bevel_factor_start" : ("Bevel Start", "Float", 0),
    "bevel_factor_end" : ("Bevel End", "Float", 1),
    "fill_mode" : ("Fill Mode", "String", "FULL")}
    
fillModes = ("FULL", "BACK", "FRONT", "HALF")  

class mn_CurveProperties(Node, AnimationNode):
    bl_idname = "mn_CurveProperties"
    bl_label = "Curve Properties"
    
    def getPossiblePropertyItems(self, context):
        items = []
        for path, (name, dataType, default) in possibleProperties.items():
            if not path in self.inputs:
                items.append((path, name, ""))
        if len(items) == 0: items.append(("NONE", "NONE", ""))
        items = sorted(items, key = lambda x: x[1])
        return items
        
    def settingChanged(self, context = None):
        for socket in self.inputs[1:]:
            socket.removeable = self.manageSockets
            socket.moveable = self.manageSockets
            
    selectedPath = EnumProperty(name = "Type", items = getPossiblePropertyItems)
    manageSockets = BoolProperty(name = "Manage Sockets", default = False, update = settingChanged, description = "Allows to move or remove sockets")
    
    errorMessage = StringProperty(default = "")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False   
        self.outputs.new("mn_ObjectSocket", "Object")
        self.width += 20
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        row.prop(self, "selectedPath", text = "")
        self.callFunctionFromUI(row, "newSocketFromSelection", text = "", icon = "PLUS")
        
        layout.prop(self, "manageSockets")
        
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")
        
    def execute(self, inputs):
        object = inputs["Object"]
        outputs = {"Object" : object}
        
        self.errorMessage = ""
        if not object: return outputs
        if object.type != "CURVE":
            self.errorMessage = "Object is no curve"
            return outputs
        if object.data.dimensions == "2D": 
            self.errorMessage = "Curve has to be 3D"
            return outputs
        if inputs.get("fill_mode", "FULL") not in fillModes:
            self.errorMessage = "Invalid fill mode"
            return outputs
        
        for path, value in inputs.items():
            if path == "Object": continue
            setattr(object.data, path, value)
        return outputs
        
    def newSocketFromSelection(self):
        path = self.selectedPath
        if path != "NONE":
            self.newSocket(path)
        
    def newSocket(self, path):
        name, dataType, default = possibleProperties[path]
        socket = self.inputs.new(getIdNameFromDataType(dataType), path)
        socket.setStoreableValue(default)
        socket.customName = name
        socket.displayCustomName = True
        self.settingChanged()
        
        # extra case to create an enum property
        if path == "fill_mode":
            socket.useEnum = True
            socket.setEnumItems([("FULL",), ("BACK",), ("FRONT",), ("HALF",)])        