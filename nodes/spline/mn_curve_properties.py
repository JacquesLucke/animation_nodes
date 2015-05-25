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
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False   
        self.outputs.new("mn_ObjectSocket", "Object")
        self.width += 20
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        row.prop(self, "selectedPath", text = "")
        props = row.operator("mn.append_curve_property_socket", text = "", icon = "PLUS")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
        layout.prop(self, "manageSockets")
        
    def execute(self, inputs):
        object = inputs["Object"]
        if getattr(object, "type", "") == "CURVE":
            for path, value in inputs.items():
                if path == "Object": continue
                setattr(object.data, path, value)
        return {"Object" : object}
        
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
        
class AppendSocket(bpy.types.Operator):
    bl_idname = "mn.append_curve_property_socket"
    bl_label = "Append Socket"
    bl_description = "Create a new socket for the selected property"
    bl_options = {"REGISTER"}
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.newSocketFromSelection()
        return {"FINISHED"}          