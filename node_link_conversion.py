import bpy
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
           
class ConvertToVector(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType in ["Integer", "Float"] and target.dataType == "Vector"
    def insert(self, nodeTree, origin, target):
        insertNode(nodeTree, "mn_CombineVector", origin, target)

class ConvertToBasicTypes(LinkCorrection):
    def check(self, origin, target):
        return target.dataType in ["String", "Integer", "Float"]
    def insert(self, nodeTree, origin, target):
        node = insertNode(nodeTree, "mn_ConvertNode", origin, target)
        node.update()
        
        
def insertNode(nodeTree, nodeType, origin, target):
    node = nodeTree.nodes.new(nodeType)
    node.select = False
    
    location = (origin.node.location + target.node.location) / 2
    node.location = location
    
    nodeTree.links.new(node.inputs[0], origin)
    nodeTree.links.new(target, node.outputs[0])
    return node
    
linkCorrectors = [cls() for cls in LinkCorrection.__subclasses__()]    