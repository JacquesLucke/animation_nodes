import bpy
from .. base_types.node import AnimationNode

class CreateAllNodes(bpy.types.Operator):
    bl_idname = "an.create_all_nodes"
    bl_label = "Create All Nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        if space.type != "NODE_EDITOR": return False
        if space.edit_tree is None: return False
        return space.edit_tree.bl_idname == "an_AnimationNodeTree"

    def execute(self, context):
        tree = context.space_data.edit_tree
        nodeClasses = AnimationNode.__subclasses__()
        for i, nodeClass in enumerate(nodeClasses):
            node = tree.nodes.new(nodeClass.bl_idname)
            node.location[0] = 300 * (i % 10)
            node.location[1] = -300 * (i // 10)
        self.report(type = {"INFO"}, message = "{} nodes created".format(len(nodeClasses)))
        return {"FINISHED"}
