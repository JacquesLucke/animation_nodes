import bpy
from .. mn_utils import *

def getAttributesFromNodesWithType(nodeType, attribute):
    data = []
    nodes = getNodesFromType(nodeType)
    for node in nodes:
        data.append(getattr(node, attribute))
    return data

def getNodeFromTypeWithAttribute(nodeType, attribute, data):
    nodes = getNodesFromTypeWithAttribute(nodeType, attribute, data)
    if len(nodes) > 0: return nodes[0]
    return None

def getNodesFromTypeWithAttribute(nodeType, attribute, data):
    nodes = []
    nodesFromType = getNodesFromType(nodeType)
    for node in nodesFromType:
        if getattr(node, attribute) == data:
            nodes.append(node)
    return nodes

def getNodesFromType(nodeType):
    nodes = []
    nodeTrees = getAnimationNodeTrees()
    for nodeTree in nodeTrees:
        for node in nodeTree.nodes:
            if node.bl_idname == nodeType:
                nodes.append(node)
    return nodes
    
def getAnimationNodeTrees():
    nodeTrees = []
    for nodeTree in bpy.data.node_groups:
        if nodeTree.bl_idname == "mn_AnimationNodeTree":
            nodeTrees.append(nodeTree)
    return nodeTrees
    
    
def getNotUsedSocketName(node, prefix = "socket name"):
    socketName = prefix
    while isSocketNameUsed(node, socketName):
        socketName = prefix + getRandomString(3)
    return socketName
def isSocketNameUsed(node, name):
    for socket in node.outputs:
        if socket.name == name or socket.identifier == name: return True
    for socket in node.inputs:
        if socket.name == name or socket.identifier == name: return True
    return False
    
    
def getNotUsedCustomSocketName(node, prefix = "custom name"):
    customName = prefix
    while isCustomSocketNameUsed(node, customName):
        customName = prefix + getRandomString(3)
    return customName
def isCustomSocketNameUsed(node, customName):
    for socket in node.outputs:
        if socket.customName == customName: return True
    return False
    
    
def removeLinksFromSocket(socket):
    if socket is None: return
    allLinks = socket.node.id_data.links
    for link in socket.links:
        allLinks.remove(link)
    

def updateDependencyNode(socket):
    if socket is not None:
        if len(socket.links) == 1:
            fromNode = socket.links[0].from_node
            if hasattr(fromNode, "update"):
                fromNode.update()
                
def isNodeRemoved(node):
    return getattr(node, "isRemoved", False)
                
                
class NodeTreeInfo:
    def __init__(self, nodeTrees):
        if isinstance(nodeTrees, (list, tuple, set)):
            self.nodes = []
            self.links = []
            for nodeTree in nodeTrees:
                self.nodes.extend(nodeTree.nodes)
                self.links.extend(nodeTree.links)
        else:
            nodeTree = nodeTrees
            self.nodes = nodeTree.nodes
            self.links = nodeTree.links
            
        self.removeDeletedObjects()
        
        self.inputSockets = {}
        self.outputSockets = {}
        self.updateSettings = {}
        
        self.createConnectionDics()
        
    def removeDeletedObjects(self):
        newNodeList = []
        for node in self.nodes:
            if not isNodeRemoved(node):
                newNodeList.append(node)
        self.nodes = newNodeList
        
        newLinkList = []
        for link in self.links:
            if not (isNodeRemoved(link.from_node) or isNodeRemoved(link.to_node)):
                newLinkList.append(link)
        self.links = newLinkList
                
    def createConnectionDics(self):
        for link in self.links:
            fromSocket = link.from_socket
            toSocket = link.to_socket
            if isReroute(toSocket): continue
            originSocket = fromSocket
            if isReroute(fromSocket): originSocket = getOriginSocket(toSocket)
            if isOtherOriginSocket(toSocket, originSocket):
                self.setConnection(originSocket, toSocket)
    def setConnection(self, fromSocket, toSocket):
        if toSocket.bl_idname == "mn_NodeNetworkSocket":
            self.updateSettings[fromSocket.node] = toSocket.node
        else:
            if fromSocket not in self.outputSockets:
                self.outputSockets[fromSocket] = []
            if toSocket not in self.inputSockets:
                self.inputSockets[toSocket] = []
            self.outputSockets[fromSocket].append(toSocket)
            self.inputSockets[toSocket].append(fromSocket)
            
    def getUpdateSettingsNode(self, node):
        return self.updateSettings.get(node)
    def isOutputSocketUsed(self, socket):
        return socket in self.outputSockets
    def hasOtherDataOrigin(self, socket):
        return self.getDataOriginSocket(socket) is not None
    def getDataOriginSockets(self, socket):
        return self.inputSockets.get(socket, [])
    def getTargetIndexFromOutputSocket(self, outputSocket, targetSocket):
        if outputSocket is None: return -1
        return self.getDataTargetSockets(outputSocket).index(targetSocket)
    def getFirstLinkedSocket(self, socket):
        if socket.is_output:
            return self.getFirstDataTargetSocket(socket)
        return self.getDataOriginSocket(socket)
    def getDataTargetSockets(self, socket):
        return self.outputSockets.get(socket, [])
    def getFirstDataTargetSocket(self, socket):
        sockets = self.getDataTargetSockets(socket)
        if len(sockets) == 0: return None
        return sockets[0]
    def getDataOriginSocket(self, socket):
        originSockets = self.inputSockets.get(socket)
        if originSockets is not None:
            return originSockets[0]
        return None
    def getDataOriginNode(self, socket):
        originSocket = self.getDataOriginSocket(socket)
        if originSocket is not None:
            return originSocket.node
        return None
    def getDirectLinkedNodes(self, node):
        linkedNodes = set()
        linkedNodes.update(self.getDirectParentNodes(node))
        linkedNodes.update(self.getDirectChildrenNodes(node))
        return linkedNodes
    def getDirectParentNodes(self, node):
        parentNodes = set()
        for socket in node.inputs:
            originSockets = self.getDataOriginSockets(socket)
            for originSocket in originSockets:
                parentNodes.update([originSocket.node])
        return parentNodes
    def getDirectChildrenNodes(self, node):
        childrenNodes = set()
        for socket in node.outputs:
            targetSockets = self.getDataTargetSockets(socket)
            for targetSocket in targetSockets:
                childrenNodes.update([targetSocket.node])
        return childrenNodes
    def getNetworkWith(self, node):
        networkNodes = []
        uncheckedNodes = [node]
        while len(uncheckedNodes) > 0:
            checkNode = uncheckedNodes[-1]
            linkedNodes = self.getDirectLinkedNodes(checkNode)
            del uncheckedNodes[-1]
            for node in linkedNodes:
                if node not in uncheckedNodes and node not in networkNodes:
                    uncheckedNodes.append(node)
            networkNodes.append(checkNode)
        return NodeNetwork(networkNodes)
    def getNetworks(self):
        networks = []
        foundNodes = []
        for node in self.nodes:
            if node not in foundNodes:
                network = self.getNetworkWith(node)
                foundNodes.extend(network.nodes)
                networks.append(network)
        return networks
        
    def get_linked_socket_pairs(self):
        pairs = []
        for node in self.nodes:
            for socket in node.outputs:
                targets = self.getDataTargetSockets(socket)
                pairs.extend([(socket, target) for target in targets])
        return pairs
    
class NodeNetwork:
    def __init__(self, nodes):
        self.nodes = nodes
        self.type = self.getNetworkType()
        
    def getLoopStartNode(self):
        if self.type != "Loop": return None
        for node in self.nodes:
            if node.bl_idname == "mn_LoopStartNode": return node
        return None
        
    def getGroupInputNode(self):
        if self.type != "Group": return None
        for node in self.nodes:
            if node.bl_idname == "mn_GroupInput": return node
        return None
    def getGroupOutputNode(self):
        if self.type != "Group": return None
        for node in self.nodes:
            if node.bl_idname == "mn_GroupOutput": return node
        return None
        
    def getNetworkType(self):
        loopStartAmount = 0
        groupInputAmount = 0
        groupOutputAmount = 0
        totalSpecials = 0
        for node in self.nodes:
            if node.bl_idname == "mn_LoopStartNode":
                loopStartAmount += 1
                totalSpecials = 1
            elif node.bl_idname == "mn_GroupInput":
                groupInputAmount += 1
                totalSpecials += 1
            elif node.bl_idname == "mn_GroupOutput":
                groupOutputAmount += 1
                totalSpecials += 1
        if totalSpecials == 0: return "Normal"
        elif loopStartAmount == 1 and totalSpecials == 1: return "Loop"
        elif (groupInputAmount == 1 and totalSpecials == 1 or
            groupInputAmount == 1 and groupOutputAmount == 1 and totalSpecials == 2): return "Group"
        if groupOutputAmount == totalSpecials: return "Ignore"
        return "Invalid"
                
        
    @staticmethod
    def fromNode(node):
        nodeTreeInfo = NodeTreeInfo(node.id_data)
        return nodeTreeInfo.getNetworkWith(node)
        
def isReroute(object):
    if isinstance(object, bpy.types.Node):
        return object.bl_idname == "NodeReroute"
    if isinstance(object, bpy.types.NodeSocket):
        return object.node.bl_idname == "NodeReroute"
    return False