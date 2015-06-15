import bpy
from . mn_execution import getCodeStrings, resetCompileBlocker, updateAnimationTrees, generateExecutionUnits
from . id_keys import getIDKeys, getIDType, getIDTypeClass
from . mn_utils import *
from . manage_broken_files import getBrokenNodes, findAndUpdateBrokenNodes, containsBrokenNodes

class BrokenNodesPanel(bpy.types.Panel):
    bl_idname = "mn.broken_nodes_panel"
    bl_label = "Broken Nodes"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Settings"
    
    @classmethod
    def poll(self, context):
        return containsBrokenNodes() and context.space_data.tree_type == "mn_AnimationNodeTree"
        
    def draw(self, context):
        layout = self.layout
        
        col = layout.column()
        for nodeTreeName, nodeName in getBrokenNodes():
            props = col.operator("mn.select_and_view_node", icon = "ERROR", text = "'{}' in '{}'".format(nodeName, nodeTreeName))
            props.nodeTreeName = nodeTreeName
            props.nodeName = nodeName
        
        layout.operator("mn.find_broken_nodes", text = "Find Missing Nodes", icon = "ZOOM_SELECTED")
        
    

class AnimationNodesPerformance(bpy.types.Panel):
    bl_idname = "mn.performance_panel"
    bl_label = "Performance"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Settings"
    
    @classmethod
    def poll(self, context):
        return context.space_data.tree_type == "mn_AnimationNodeTree"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        col.scale_y = 1.3
        col.operator("mn.force_full_update", text = "Force Update", icon = "PLAY")
        
        col = layout.column(align = True)
        col.prop(scene.mn_settings.update, "frameChange", text = "Frame Changed")
        col.prop(scene.mn_settings.update, "sceneUpdate", text = "Scene Changed")
        col.prop(scene.mn_settings.update, "propertyChange", text = "Property Changed")
        col.prop(scene.mn_settings.update, "resetCompileBlockerWhileRendering", text = "Is Rendering")
        layout.prop(scene.mn_settings.update, "skipFramesAmount")
        layout.prop(scene.mn_settings.update, "redrawViewport")
    
class AnimationNodesDeveloperPanel(bpy.types.Panel):
    bl_idname = "mn.developer_panel"
    bl_label = "Developer"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Settings"
    
    @classmethod
    def poll(self, context):
        return context.space_data.tree_type == "mn_AnimationNodeTree"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align = True)
        col.operator("mn.unit_execution_code_in_text_block")
        col.operator("mn.print_node_tree_execution_string")
        
        col = layout.column(align = True)
        col.prop(scene.mn_settings.developer, "printUpdateTime", text = "Print Update Time")
        col.prop(scene.mn_settings.developer, "printGenerationTime", text = "Print Generation Time")
        col.prop(scene.mn_settings.developer, "executionProfiling", text = "Node Execution Profiling")
        
class NodePropertiesPanel(bpy.types.Panel):
    bl_idname = "mn.node_properties_panel"
    bl_label = "Node and Socket Settings"
    bl_space_type = "NODE_EDITOR"   
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return context.active_node
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self.node, "bl_width_max", text = "Max Width")
        self.drawSocketVisibility(layout)
        
    def drawSocketVisibility(self, layout):
        row = layout.row(align = False)
        
        col = row.column(align = True)
        col.label("Inputs:")
        for socket in self.node.inputs:
            col.prop(socket, "show", text = socket.name)
            
        col = row.column(align = True)
        col.label("Outputs:")
        for socket in self.node.outputs:
            col.prop(socket, "show", text = socket.name)
            
    @property
    def node(self):
        return bpy.context.active_node
        
class IDKeysManagerPanel(bpy.types.Panel):
    bl_idname = "mn.id_keys_manager"
    bl_label = "ID Keys Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"
        
    def draw(self, context):
        layout = self.layout
        idKeySettings = context.scene.mn_settings.idKeys
        
        box = layout.box()
        
        for keyName, keyType in getIDKeys():
            row = box.row()
            row.label(keyName)
            row.label(keyType)
            props = row.operator("mn.remove_id_key", icon = "X", text = "")
            props.name = keyName
            
        row = layout.row(align = True)
        row.prop(idKeySettings, "new_key_name", text = "")
        row.prop(idKeySettings, "new_key_type", text = "")
        row.operator("mn.new_id_key", icon = "SAVE_COPY", text = "")
        
class IDKeyPanel(bpy.types.Panel):
    bl_idname = "mn.keyframes"
    bl_label = "Keyframes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"
        
    @classmethod
    def poll(cls, context):
        return context.active_object
        
    def draw(self, context):
        layout = self.layout
        object = context.active_object
        
        for keyName, keyType in getIDKeys():
            box = layout.box()
            row = box.row()
            subRow = row.row()
            subRow.alignment = "LEFT"
            subRow.label(keyName)
            subRow = row.row()
            subRow.alignment = "RIGHT"
            subRow.label(keyType)
            
            typeClass = getIDTypeClass(keyType)
            if typeClass.exists(object, keyName):
                typeClass.draw(box, object, keyName)
            else:
                row = box.row()
                row.label("Does not exist", icon = "ERROR")
                props = row.operator("mn.create_key_on_object")
                props.name = keyName
                props.type = keyType
                props.objectName = object.name
        
        
class ForceNodeTreeUpdate(bpy.types.Operator):
    bl_idname = "mn.force_full_update"
    bl_label = "Force Node Tree Update"
    bl_description = "Recalculate the nodes / Start the execution again after an error happened"

    def execute(self, context):
        resetCompileBlocker()
        generateExecutionUnits()
        updateAnimationTrees()
        return {'FINISHED'}
        
class PrintNodeTreeExecutionStrings(bpy.types.Operator):
    bl_idname = "mn.print_node_tree_execution_string"
    bl_label = "Print Node Tree Code"
    bl_description = "Print the auto generated python code into the console"

    def execute(self, context):
        print()
        for codeString in getCodeStrings():
            print(codeString)
            print()
            print("-"*80)
            print()
        return {'FINISHED'}
        
class UnitExecutionCodeInTextBlock(bpy.types.Operator):
    bl_idname = "mn.unit_execution_code_in_text_block"
    bl_label = "Code in Text Block"
    bl_description = "Create a text block and insert the auto generated python code"
    
    def execute(self, context):
        codeString = ("\n\n#"+ "-"*50 + "\n\n").join(getCodeStrings())
        textBlock = bpy.data.texts.get("Unit Execution Code")
        if textBlock is None:
            textBlock = bpy.data.texts.new("Unit Execution Code")
        textBlock.from_string(codeString)
        return {'FINISHED'}