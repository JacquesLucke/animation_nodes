import bpy
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class an_ObjectNameFilterNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectNameFilterNode"
    bl_label = "Object Name Filter"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()
    
    useAllInScene = bpy.props.BoolProperty(default = False, description = "Use All Objects In Scene instead of socket", update = checkedPropertiesChanged)
    useCaseSensitive = bpy.props.BoolProperty(default = False, description = "Use Case Sensitive", update = checkedPropertiesChanged)
    
    filterType = bpy.props.EnumProperty(items = [("STARTS WITH", "Starts With", "All Objects with names starting with"),
                                                 ("ENDS WITH", "Ends With", "All Objects with names ending with")],
                                        update = checkedPropertiesChanged, default = "STARTS WITH")
    
    def create(self):
        self.bl_width_default = 160
        self.width = 160
        self.inputs.new("an_ObjectListSocket", "Objects", "objects")
        self.inputs.new("an_StringSocket", "Name", "name")
        self.outputs.new("an_ObjectListSocket", "Objects", "objects")
        self.outputs.new("an_StringListSocket", "Names", "names").hide = True
        self.updateSocketVisibility()
        
    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "filterType", text = "Type", expand = True)

        row = col.row(align = True)
        row.prop(self, "useAllInScene", text = "All Scene Objects", icon = "SCENE_DATA")
        row.prop(self, "useCaseSensitive", text = "", icon = "FONTPREVIEW")
        
    def updateSocketVisibility(self):
        self.inputs["Objects"].hide = self.useAllInScene

    def getExecutionCode(self):

        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        lines = []
        lines.append("obList = []")
        if self.useAllInScene: lines.append("obList = bpy.context.scene.objects")
        else: lines.append("if objects is not None: obList = objects")
    
        lines.append("filteredObjects, filteredNames = [], []")
        if self.useCaseSensitive: 
            if self.filterType == "STARTS WITH": 
                lines.append("filteredObjects = [ob for ob in obList if ob.name.startswith(str(name))]")
            if self.filterType == "ENDS WITH": 
                lines.append("filteredObjects = [ob for ob in obList if ob.name.endswith(str(name))]")
        else: 
            if self.filterType == "STARTS WITH": 
                lines.append("filteredObjects = [ob for ob in obList if ob.name.lower().startswith(str.lower(name))]")
            if self.filterType == "ENDS WITH": 
                lines.append("filteredObjects = [ob for ob in obList if ob.name.lower().endswith(str.lower(name))]")
        
        lines.append("filteredNames = [ob.name for ob in filteredObjects]")
        lines.append("objects, names = filteredObjects, filteredNames")
        
        return lines