import bpy

def subprograms_menu_callback(self, context):
    if context.space_data.tree_type != "an_AnimationNodeTree": return
    self.layout.menu("AN_MT_subprograms_menu", text="Subprograms")

def remove_nodetree_callback(self, context):
    if context.space_data.tree_type != "an_AnimationNodeTree": return
    self.layout.operator("an.remove_node_tree", text="Remove", icon="CANCEL")

def register():
    bpy.types.NODE_MT_editor_menus.append(subprograms_menu_callback)
    bpy.types.NODE_HT_header.append(remove_nodetree_callback)

def unregister():
    bpy.types.NODE_MT_editor_menus.remove(subprograms_menu_callback)
    bpy.types.NODE_HT_header.remove(remove_nodetree_callback)
