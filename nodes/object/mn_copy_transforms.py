import bpy, time
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... utils.fcurve import *
from ... mn_utils import *
from ... mn_cache import *

class mn_CopyTransformsNode(Node, AnimationNode):
    bl_idname = "mn_CopyTransformsNode"
    bl_label = "Copy Transforms"
    
    useLocation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
    useRotation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
    useScale = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
    
    frameTypes = [
        ("OFFSET", "Offset", ""),
        ("ABSOLUTE", "Absolute", "") ]
    frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "From")
        self.inputs.new("mn_ObjectSocket", "To")
        self.inputs.new("mn_FloatSocket", "Frame")
        self.outputs.new("mn_ObjectSocket", "To")
        self.width = 200
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        
        row = col.row(align = True)
        row.label("Location")
        row.prop(self, "useLocation", index = 0, text = "X")
        row.prop(self, "useLocation", index = 1, text = "Y")
        row.prop(self, "useLocation", index = 2, text = "Z")
        row = col.row(align = True)
        row.label("Rotation")
        row.prop(self, "useRotation", index = 0, text = "X")
        row.prop(self, "useRotation", index = 1, text = "Y")
        row.prop(self, "useRotation", index = 2, text = "Z")
        row = col.row(align = True)
        row.label("Scale")
        row.prop(self, "useScale", index = 0, text = "X")
        row.prop(self, "useScale", index = 1, text = "Y")
        row.prop(self, "useScale", index = 2, text = "Z")
        
        layout.prop(self, "frameTypesProperty")
        
    def getInputSocketNames(self):
        return {"From" : "fromObject",
                "To" : "toObject",
                "Frame" : "frame"}
    def getOutputSocketNames(self):
        return {"To" : "toObject"}
        
    def execute(self, fromObject, toObject, frame):
        if fromObject is None or toObject is None:
            return toObject
            
        if self.frameTypesProperty == "OFFSET":
            frame += getCurrentFrame()
    
        useLoc = self.useLocation
        useRot = self.useRotation
        useScale = self.useScale
        
        # location
        if useLoc[0] and useLoc[1] and useLoc[2]:
            toObject.location = getArrayValueAtFrame(fromObject, "location", frame)
        elif useLoc[0] and useLoc[1]:
            [toObject.location[0], toObject.location[1]] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [0, 1], frame)
        elif useLoc[0] and useLoc[2]:
            [toObject.location[0], toObject.location[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [0, 2], frame)
        elif useLoc[1] and useLoc[2]:
            [toObject.location[1], toObject.location[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [1, 2], frame)
        else:
            for i in range(3):
                if useLoc[i]: toObject.location[i] = getSingleValueOfArrayAtFrame(fromObject, "location", index = i, frame = frame)
                
        # rotation
        if useRot[0] and useRot[1] and useRot[2]:
            toObject.rotation_euler = getArrayValueAtFrame(fromObject, "rotation_euler", frame)
        elif useRot[0] and useRot[1]:
            [toObject.rotation_euler[0], toObject.rotation_euler[1]] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [0, 1], frame)
        elif useRot[0] and useRot[2]:
            [toObject.rotation_euler[0], toObject.rotation_euler[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [0, 2], frame)
        elif useRot[1] and useRot[2]:
            [toObject.rotation_euler[1], toObject.rotation_euler[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [1, 2], frame)
        else:
            for i in range(3):
                if useRot[i]: toObject.rotation_euler[i] = getSingleValueOfArrayAtFrame(fromObject, "rotation_euler", index = i, frame = frame)
                
        # scale
        if useScale[0] and useScale[1] and useScale[2]:
            toObject.scale = getArrayValueAtFrame(fromObject, "scale", frame)
        elif useScale[0] and useScale[1]:
            [toObject.scale[0], toObject.scale[1]] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [0, 1], frame)
        elif useScale[0] and useScale[2]:
            [toObject.scale[0], toObject.scale[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [0, 2], frame)
        elif useScale[1] and useScale[2]:
            [toObject.scale[1], toObject.scale[2]] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [1, 2], frame)
        else:
            for i in range(3):
                if useScale[i]: toObject.scale[i] = getSingleValueOfArrayAtFrame(fromObject, "scale", index = i, frame = frame)
                    
        return toObject
