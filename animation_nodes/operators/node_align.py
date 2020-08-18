import bpy
from mathutils import Vector
from .. preferences import getPieMenuSettings
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
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        alignDependent(offset, getNodesWhenFollowingBranchedLinks(activeNode, followOutputs = True))
        return {"FINISHED"}

def alignDependent(offset, nodes):
        activeNode = nodes[0]
        activeLocation = activeNode.location
        xOffset = activeNode.width / 2
        yOffset = activeNode.height / 2
        lastNode = activeNode
        for node in nodes[1:]:
            if type(node) == list:
                alignDependent(offset, node)
            else:
                widthOffset = node.width / 2
                xOffset += widthOffset + offset
                if node.type != 'REROUTE':
                    if lastNode.type == 'REROUTE':
                        activeLocation = node.location
                        xOffset = node.width / 2
                        yOffset = node.height / 2
                    else:
                        node.location = activeLocation + Vector((xOffset, yOffset - node.height / 2))
                        xOffset += widthOffset
                lastNode = node

class AlignDependenciesNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_dependencies"
    bl_label = "Align Dependencies"

    def execute(self, context):
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        alignDependencies(offset, getNodesWhenFollowingBranchedLinks(activeNode, followInputs = True))
        return {"FINISHED"}

def alignDependencies(offset, nodes):
        activeNode = nodes[0]
        activeLocation = activeNode.location
        xOffset = activeNode.width / 2
        yOffset = activeNode.height / 2
        lastNode = activeNode
        for node in nodes[1:]:
            if type(node) == list:
                alignDependencies(offset, node)
            else:
                widthOffset = node.width / 2
                xOffset += widthOffset + offset
                if node.type != 'REROUTE':
                    if lastNode.type == 'REROUTE':
                        activeLocation = node.location
                        xOffset = node.width / 2
                        yOffset = node.height / 2
                    else:
                        node.location = activeLocation + Vector((- xOffset, yOffset - node.height / 2))
                        xOffset += widthOffset
                lastNode = node

class AlignTopSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_top_selection_nodes"
    bl_label = "Align Top Selection Nodes"

    def execute(self, context):
        activeNode = context.active_node
        previousNode = activeNode

        for node in context.selected_nodes:
            if node != activeNode:
                node.location.y = previousNode.location.y
                previousNode = node
        return {"FINISHED"}

class AlignLeftSideSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_left_side_selection_nodes"
    bl_label = "Align Left Side Selection Nodes"

    def execute(self, context):
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        previousNode = activeNode

        for node in context.selected_nodes:
            if node != activeNode:
                node.location.x = getNodeLeftOffset(previousNode, node, offset)
                previousNode = node
        return {"FINISHED"}

def getNodeLeftOffset(previousNode, node, offset):
    if node.type == "REROUTE":
        return previousNode.location.x - offset
    return previousNode.location.x - (node.width + offset)

class AlignRightSideSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.align_right_side_selection_nodes"
    bl_label = "Align Right Side Selection Nodes"

    def execute(self, context):
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        previousNode = activeNode

        for node in context.selected_nodes:
            if node != activeNode:
                node.location.x = getNodeRightOffset(previousNode, offset)
                previousNode = node
        return {"FINISHED"}

def getNodeRightOffset(previousNode, offset):
    if previousNode.type == "REROUTE":
        return previousNode.location.x + offset
    return previousNode.location.x + previousNode.width + offset

class StakeUpSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.stake_up_selection_nodes"
    bl_label = "Stake Up Selection Nodes"

    def execute(self, context):
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        previousNode = activeNode

        for node in context.selected_nodes:
            if node != activeNode:
                node.location = getNodeStakeUpLocation(previousNode, node, offset)
                previousNode = node
        return {"FINISHED"}

def getNodeStakeUpLocation(previousNode, node, offset):
    location = previousNode.location.copy()
    if node.type == "REROUTE":
        location.y += offset
        return location
    location.y += node.dimensions.y + offset
    return location

class StakeDownSelectionNodes(bpy.types.Operator, NodeOperator):
    bl_idname = "an.stake_down_selection_nodes"
    bl_label = "Stake Down Selection Nodes"

    def execute(self, context):
        offset = getPieMenuSettings().offset
        activeNode = context.active_node
        previousNode = activeNode

        for node in context.selected_nodes:
            if node != activeNode:
                node.location = getNodeStakeDownLocation(previousNode, offset)
                previousNode = node
        return {"FINISHED"}

def getNodeStakeDownLocation(previousNode, offset):
    location = previousNode.location.copy()
    if previousNode.type == "REROUTE":
        location.y -= offset
        return location
    location.y -= previousNode.dimensions.y + offset
    return location

def getNodesWhenFollowingBranchedLinks(startNode, followInputs = False, followOutputs = False):
    nodes = []
    nodesToCheck = {startNode}
    while nodesToCheck:
        node = nodesToCheck.pop()
        nodes.append(node)
        sockets = []
        if followInputs:
            sockets.extend(node.inputs)
            nodesLinked = getLinkedNodes(sockets)
            if len(nodesLinked) > 1:
                for node in nodesLinked:
                    nodes.append(getNodesWhenFollowingBranchedLinks(node, followInputs, followOutputs))
            else:
                for node in nodesLinked:
                    if node not in nodes: nodesToCheck.add(node)

        if followOutputs:
            sockets.extend(node.outputs)
            for socket in sockets:
                linkedSockets = getDirectlyLinkedSockets(socket)
                if len(linkedSockets) > 1 or isMultiLinkedSockets(sockets):
                    for linkedSocket in linkedSockets:
                        node = linkedSocket.node
                        nodes.append(getNodesWhenFollowingBranchedLinks(node, followInputs, followOutputs))
                else:
                    for linkedSocket in linkedSockets:
                        node = linkedSocket.node
                        if node not in nodes: nodesToCheck.add(node)
    return nodes

def getLinkedNodes(sockets):
    nodesLinked = []
    for socket in sockets:
        linkedSockets = getDirectlyLinkedSockets(socket)
        for linkedSocket in linkedSockets:
            node = linkedSocket.node
            if node not in nodesLinked: nodesLinked.append(node)
    return nodesLinked

def isMultiLinkedSockets(sockets):
    count = 0
    for socket in sockets:
       if len(getDirectlyLinkedSockets(socket)): count += 1
       if count > 1: return True
    return False
