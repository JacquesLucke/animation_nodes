import bpy

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
        col = layout.column()
        col.prop(self.node, "width", text = "Width")
        col.prop(self.node, "bl_width_max", text = "Max Width")
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
