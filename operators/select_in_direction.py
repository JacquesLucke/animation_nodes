import bpy
from . an_operator import AnimationNodeOperator

class SelectDependentNodes(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.select_dependent_nodes"
    bl_label = "Select Dependent Nodes"

    def execute(self, context):
        for node in context.active_node.getNodesWhenFollowingLinks(followOutputs = True):
            node.select = True
        return {"FINISHED"}

class SelectDependenciesNodes(bpy.types.Operator, AnimationNodeOperator):
    bl_idname = "an.select_dependencies"
    bl_label = "Select Dependencies"

    def execute(self, context):
        for node in context.active_node.getNodesWhenFollowingLinks(followInputs = True):
            node.select = True
        return {"FINISHED"}
