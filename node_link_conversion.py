import bpy
from mathutils import Vector
from . utils.nodes import *
from . sockets.info import toBaseIdName

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

class ConvertParticleSystemToParticle(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Particle System" and target.dataType == "Particle"
    def insert(self, nodeTree, origin, target):
        systemInfo, listElement = insertNodes(nodeTree, ["mn_GetParticles", "mn_GetListElementNode"], origin, target)
        listElement.generateSockets(listIdName = "mn_ParticleListSocket")
        nodeTree.links.new(systemInfo.inputs[0], origin)
        nodeTree.links.new(listElement.inputs[0], systemInfo.outputs[0])
        nodeTree.links.new(listElement.outputs[0], target)

class ConvertParticleSystemToParticles(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Particle System" and target.dataType == "Particle List"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_GetParticles", origin, target)

class ConvertListToElement(LinkCorrection):
    def check(self, origin, target):
        return toBaseIdName(origin.bl_idname) == target.bl_idname
    def insert(self, nodeTree, origin, target):
        node = insertNode(nodeTree, "mn_GetListElementNode", origin, target)
        node.generateSockets(listIdName = origin.bl_idname)
        insertBasicLinking(nodeTree, origin, node, target)

class ConvertElementToList(LinkCorrection):
    def check(self, origin, target):
        return origin.bl_idname == toBaseIdName(target.bl_idname)
    def insert(self, nodeTree, origin, target):
        node = insertNode(nodeTree, "mn_CreateList", origin, target)
        node.assignListType(origin.dataType, inputAmount = 1)
        insertBasicLinking(nodeTree, origin, node, target)

class ConvertMeshDataToMesh(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Mesh Data" and target.dataType == "Mesh"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_CreateMeshFromData", origin, target)

class ConvertMeshDataToVertexLocations(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Mesh Data" and target.dataType == "Vector List"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_SeparateMeshData", origin, target)

class ConvertVertexLocationsToMeshData(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector List" and target.dataType == "Mesh Data"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_CombineMeshData", origin, target)

class ConvertPolygonListIndicesToEdgeListIndices(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Polygon Indices List" and target.dataType == "Edge Indices List"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_EdgesOfPolygons", origin, target)

class ConvertSeparatedMathDataToMesh(LinkCorrection):
    separatedMeshDataTypes = ["Vector List", "Edge Indices List", "Polygon Indices List"]
    def check(self, origin, target):
        return origin.dataType in self.separatedMeshDataTypes and target.dataType == "Mesh"
    def insert(self, nodeTree, origin, target):
        toMeshData, toMesh = insertNodes(nodeTree, ["mn_CombineMeshData", "mn_CreateMeshFromData"], origin, target)
        nodeTree.links.new(toMeshData.inputs[self.separatedMeshDataTypes.index(origin.dataType)], origin)
        nodeTree.links.new(toMesh.inputs[0], toMeshData.outputs[0])
        nodeTree.links.new(toMesh.outputs[0], target)

class ConvertToVector(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType in ["Integer", "Float"] and target.dataType == "Vector"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_CombineVector", origin, target)

class ConvertVectorToNumber(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector" and target.dataType == "Float"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_SeparateVector", origin, target)

class ConvertTextBlockToString(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Text Block" and target.dataType == "String"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_TextBlockReader", origin, target)

class ConvertVectorToMatrix(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector" and target.dataType == "Matrix"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_TranslationMatrix", origin, target)

class ConvertListToLength(LinkCorrection):
    def check(self, origin, target):
        return "List" in origin.dataType and target.dataType == "Integer"
    def insert(self, nodeTree, origin, target):
        insertLinkedNode(nodeTree, "mn_GetListLengthNode", origin, target)

class ConverFloatToInteger(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Float" and target.dataType == "Integer"
    def insert(self, nodeTree, origin, target):
        node = insertLinkedNode(nodeTree, "mn_FloatToInteger", origin, target)

class ConvertToBasicTypes(LinkCorrection):
    def check(self, origin, target):
        return target.dataType in ["String", "Integer", "Float"]
    def insert(self, nodeTree, origin, target):
        node = insertLinkedNode(nodeTree, "mn_ConvertNode", origin, target)
        node.edit()

class ConvertFromGeneric(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Generic"
    def insert(self, nodeTree, origin, target):
        node = insertLinkedNode(nodeTree, "mn_ConvertNode", origin, target)
        node.edit()


def insertLinkedNode(nodeTree, nodeType, origin, target):
    node = insertNode(nodeTree, nodeType, origin, target)
    insertBasicLinking(nodeTree, origin, node, target)
    return node

def insertNode(nodeTree, nodeType, leftSocket, rightSocket):
    nodes = insertNodes(nodeTree, [nodeType], leftSocket, rightSocket)
    return nodes[0]

def insertNodes(nodeTree, nodeTypes, leftSocket, rightSocket):
    center = getSocketCenter(leftSocket, rightSocket)
    amount = len(nodeTypes)
    nodes = []
    for i, nodeType in enumerate(nodeTypes):
        node = nodeTree.nodes.new(nodeType)
        node.select = False
        node.location = center + Vector((180 * (i - (amount - 1) / 2), 0))
        nodes.append(node)
    return nodes

def insertBasicLinking(nodeTree, originSocket, node, targetSocket):
    nodeTree.links.new(node.inputs[0], originSocket)
    nodeTree.links.new(targetSocket, node.outputs[0])

def getSocketCenter(socket1, socket2):
    return (socket1.node.location + socket2.node.location) / 2

linkCorrectors = [
    ConvertParticleSystemToParticle(),
    ConvertParticleSystemToParticles(),
    ConvertListToElement(),
    ConvertElementToList(),
    ConvertMeshDataToMesh(),
    ConvertMeshDataToVertexLocations(),
    ConvertVertexLocationsToMeshData(),
    ConvertPolygonListIndicesToEdgeListIndices(),
    ConvertSeparatedMathDataToMesh(),
    ConvertToVector(),
    ConvertVectorToNumber(),
    ConvertTextBlockToString(),
    ConvertVectorToMatrix(),
	ConvertListToLength(),
    ConverFloatToInteger(),
    ConvertToBasicTypes(),
    ConvertFromGeneric() ]
