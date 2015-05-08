import bpy
from mathutils import Vector
from . utils.mn_node_utils import *

def correctForbiddenNodeLinks():
    nodeTree = NodeTreeInfo(getAnimationNodeTrees())
    linked_sockets = nodeTree.get_linked_socket_pairs()
    invalid_links = filterInvalidLinks(linked_sockets)
    for pair in invalid_links:
        nodeTree = pair[0].node.id_data
        origin = pair[1].links[0].from_socket
        is_corrected = False
        for corrector in linkCorrectors:
            if corrector.check(*pair):
                corrector.insert(nodeTree, origin, pair[1])
                is_corrected = True
                break
        if not is_corrected:
            removeLink(*pair)
            
def filterInvalidLinks(linked_sockets):
    return [pair for pair in linked_sockets if not isConnectionValid(*pair)]
        
def isConnectionValid(origin, target):
    return origin.dataType in target.allowedInputTypes or target.allowedInputTypes[0] == "all"    
    
def removeLink(origin, target):
    nodeTree = origin.node.id_data
    for link in nodeTree.links:
        if link.from_socket == origin and link.to_socket == target:
            nodeTree.links.remove(link)
                    
                    
class LinkCorrection:
    # subclasses need a check and insert function
    pass
    
class ConvertMeshDataToMesh(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Mesh Data" and target.dataType == "Mesh"
    def insert(self, nodeTree, origin, target):
        insertNode(nodeTree, "mn_CreateMeshFromData", origin, target)

class ConvertVertexLocationsToMesh(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector List" and target.dataType == "Mesh"
    def insert(self, nodeTree, origin, target):
        center = getSocketCenter(origin, target)
            
        toMeshData = nodeTree.nodes.new("mn_CombineMeshData")
        toMesh = nodeTree.nodes.new("mn_CreateMeshFromData")
        
        toMeshData.location = center - Vector((90, 0))
        toMesh.location = center + Vector((90, 0))
        
        nodeTree.links.new(toMeshData.inputs[0], origin)
        nodeTree.links.new(toMesh.inputs[0], toMeshData.outputs[0])
        nodeTree.links.new(toMesh.outputs[0], target)
           
class ConvertToVector(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType in ["Integer", "Float"] and target.dataType == "Vector"
    def insert(self, nodeTree, origin, target):
        insertNode(nodeTree, "mn_CombineVector", origin, target)
        
class ConvertVectorToNumber(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector" and target.dataType == "Float"
    def insert(self, nodeTree, origin, target):
        insertNode(nodeTree, "mn_SeparateVector", origin, target)        

class ConvertToBasicTypes(LinkCorrection):
    def check(self, origin, target):
        return target.dataType in ["String", "Integer", "Float"]
    def insert(self, nodeTree, origin, target):
        node = insertNode(nodeTree, "mn_ConvertNode", origin, target)
        node.update()
        
        
def insertNode(nodeTree, nodeType, origin, target):
    node = nodeTree.nodes.new(nodeType)
    node.select = False
    
    location = getSocketCenter(origin, target)
    node.location = location 
    
    nodeTree.links.new(node.inputs[0], origin)
    nodeTree.links.new(target, node.outputs[0])
    return node
    
def getSocketCenter(socket1, socket2):
    return (socket1.node.location + socket2.node.location) / 2
    
linkCorrectors = [
    ConvertMeshDataToMesh(),
    ConvertVertexLocationsToMesh(),
    ConvertToVector(),
    ConvertVectorToNumber(),
    ConvertToBasicTypes()]