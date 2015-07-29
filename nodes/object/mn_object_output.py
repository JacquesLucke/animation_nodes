import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_ObjectTransformsOutput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ObjectTransformsOutput"
    bl_label = "Transforms Output"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    useLocation = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)
    useRotation = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)
    useScale = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_VectorSocket", "Location")
        self.inputs.new("mn_VectorSocket", "Rotation")
        self.inputs.new("mn_VectorSocket", "Scale").vector = (1, 1, 1)
        self.outputs.new("mn_ObjectSocket", "Object")
        self.updateSocketVisibility()
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
        
    def updateSocketVisibility(self):
        self.inputs["Location"].hide = not (self.useLocation[0] or self.useLocation[1] or self.useLocation[2])
        self.inputs["Rotation"].hide = not (self.useRotation[0] or self.useRotation[1] or self.useRotation[2])
        self.inputs["Scale"].hide = not (self.useScale[0] or self.useScale[1] or self.useScale[2])
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Location" : "location",
                "Rotation" : "rotation",
                "Scale" : "scale"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        useLoc = self.useLocation
        useRot = self.useRotation
        useScale = self.useScale
        
        codeLines = []
        codeLines.append("if %object% is not None:")
        
        # location
        if useLoc[0] and useLoc[1] and useLoc[2]:
            codeLines.append("    %object%.location = %location%")
        else:
            for i in range(3):
                if useLoc[i]: codeLines.append("    %object%.location["+str(i)+"] = %location%["+str(i)+"]")
                
        # rotation
        if useRot[0] and useRot[1] and useRot[2]:
            codeLines.append("    %object%.rotation_euler = %rotation%")
        else:
            for i in range(3):
                if useRot[i]: codeLines.append("    %object%.rotation_euler["+str(i)+"] = %rotation%["+str(i)+"]")
        
        # scale
        if useScale[0] and useScale[1] and useScale[2]:
            codeLines.append("    %object%.scale = %scale%")
        else:
            for i in range(3):
                if useScale[i]: codeLines.append("    %object%.scale["+str(i)+"] = %scale%["+str(i)+"]")
        
        if not (useLoc[0] or useLoc[1] or useLoc[2] or
                useRot[0] or useRot[1] or useRot[2] or
                useScale[0] or useScale[1] or useScale[2]):
            codeLines = []
            
        codeLines.append("$object$ = %object%")
        return "\n".join(codeLines)

