import bpy
from mathutils import Vector
from .. tree_info import getDirectlyLinkedSockets

class NodeOperator:
    @classmethod
    def poll(cls, context):
        tree = context.getActiveAnimationNodeTree()
        if tree is None: return False
        if tree.nodes.active is None: return False
        return True

class AlignDependentNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_dependent_nodes"
    bl_label = "Align Dependent Nodes"

    def execute(self, context):
        offset = 20
        activeNode = context.active_node
        activeNodeWidth = activeNode.width
        activeNodeHeight = activeNode.height
        activeNodeCenter = activeNode.location
        xOffset = activeNodeWidth / 2
        yOffset = activeNodeHeight / 2
        for node in getNodesWhenFollowingLinks(activeNode, followOutputs = True):
            widthOffset = node.width / 2
            xOffset += widthOffset + offset
            node.location = activeNodeCenter + Vector((xOffset, yOffset - node.height / 2))
            xOffset += widthOffset
        return {"FINISHED"}

class AlignDependenciesNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_dependencies"
    bl_label = "Align Dependencies"

    def execute(self, context):
        offset = 20
        activeNode = context.active_node
        activeNodeWidth = activeNode.width
        activeNodeHeight = activeNode.height
        activeNodeCenter = activeNode.location
        xOffset = activeNodeWidth / 2
        yOffset = activeNodeHeight / 2
        for node in getNodesWhenFollowingLinks(context.active_node, followInputs = True):
            widthOffset = node.width / 2
            xOffset += widthOffset + offset
            node.location = activeNodeCenter + Vector((- xOffset, yOffset - node.height / 2))
            xOffset += widthOffset
        return {"FINISHED"}

class AlignTopSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_top_selection_nodes"
    bl_label = "Align Top Selection Nodes"

    def execute(self, context):
        activeNode = context.active_node
        activeNodeCenter = activeNode.location
        yOffset = activeNode.height / 2
        for node in context.selected_nodes:
            if node != activeNode:
                location = node.location
                node.location = Vector((location.x, activeNodeCenter.y + yOffset - node.height / 2))
        return {"FINISHED"}

class AlignDownSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_down_selection_nodes"
    bl_label = "Align Down Selection Nodes"

    def execute(self, context):
        offset = 20
        activeNode = context.active_node
        location = activeNode.location.copy()
        yOffset = activeNode.dimensions.y
        for node in context.selected_nodes:
            if node != activeNode:
                location.y += -(yOffset + offset)
                node.location = location
                yOffset = node.dimensions.y
        return {"FINISHED"}

def getNodesWhenFollowingLinks(startNode, followInputs = False, followOutputs = False):
    nodes = []
    nodesToCheck = {startNode}
    while nodesToCheck:
        node = nodesToCheck.pop()
        nodes.append(node)
        sockets = []
        if followInputs: sockets.extend(node.inputs)
        if followOutputs: sockets.extend(node.outputs)
        for socket in sockets:
            for linkedSocket in getDirectlyLinkedSockets(socket):
                node = linkedSocket.node
                if node not in nodes: nodesToCheck.add(node)
    nodes.remove(startNode)
    return nodes
