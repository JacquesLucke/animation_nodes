import bpy
from bpy.props import StringProperty


class FrameSelected(bpy.types.Operator):
    bl_idname = "an.frame_selected"
    bl_label = "Frame Selected"
    bl_description = ""

    label_prop: StringProperty(
        name='Frame',
        description='Frame',
        default='Frame'
    )

    def execute(self, context):

        nodes = context.space_data.node_tree.nodes
        selected = []
        for node in nodes:
            if node.select == True:
                selected.append(node)

        bpy.ops.node.add_node(type='NodeFrame')
        frm = nodes.active
        frm.label = self.label_prop

        for node in selected:
            node.parent = frm

        return {'FINISHED'}
