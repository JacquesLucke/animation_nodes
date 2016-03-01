import bpy
from .. tree_info import getNetworkByIdentifier

class MoveViewToSubprogram(bpy.types.Operator):
    bl_idname = "an.move_view_to_subprogram"
    bl_label = "Move View to Subprogram"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        try: return context.active_node.bl_idname == "an_InvokeSubprogramNode"
        except: return False

    def execute(self, context):
        invokerNode = context.active_node
        try:
            network = getNetworkByIdentifier(invokerNode.subprogramIdentifier)
            context.space_data.node_tree = network.nodeTree
            bpy.ops.node.select_all(action = "DESELECT")
            for node in network.getNodes():
                node.select = True
            bpy.ops.node.view_selected()
            return {"FINISHED"}
        except:
            self.report({"ERROR"}, "This node is not linked to a subprogram")
            return {"CANCELLED"}
