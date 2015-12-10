import bpy
from . import tree_info
from mathutils import Vector
from . sockets.info import toBaseIdName, isList
from . tree_info import getAllDataLinks, getDirectlyLinkedSocket

def correctForbiddenNodeLinks():
    dataLinks = getAllDataLinks()
    invalidLinks = filterInvalidLinks(dataLinks)
    for dataOrigin, target in invalidLinks:
        directOrigin = getDirectlyLinkedSocket(target)
        if not tryToCorrectLink(dataOrigin, directOrigin, target):
            removeLink(directOrigin, target)
    tree_info.updateIfNecessary()

def filterInvalidLinks(dataLinks):
    return [dataLink for dataLink in dataLinks if not isConnectionValid(*dataLink)]

def isConnectionValid(origin, target):
    return origin.dataType in target.allowedInputTypes or target.allowedInputTypes[0] == "all"

def tryToCorrectLink(dataOrigin, directOrigin, target):
    for corrector in linkCorrectors:
        if corrector.check(dataOrigin, target):
            nodeTree = target.getNodeTree()
            corrector.insert(nodeTree, directOrigin, target, dataOrigin)
            return True
    return False

def removeLink(origin, target):
    nodeTree = origin.getNodeTree()
    for link in nodeTree.links:
        if link.from_socket == origin and link.to_socket == target:
            nodeTree.links.remove(link)


class LinkCorrection:
    # subclasses need a check and insert function
    pass

class SimpleConvert(LinkCorrection):
    rules = {
        ("Boolean", "Integer") : "an_BooleanToIntegerNode",
        ("Boolean", "Float") : "an_BooleanToIntegerNode",
        ("Float", "Integer") : "an_FloatToIntegerNode",
        ("Vector", "Matrix") : "an_TranslationMatrixNode",
        ("Text Block", "String") : "an_TextBlockReaderNode",
        ("Vector", "Float") : "an_SeparateVectorNode",
        ("Float", "Vector") : "an_CombineVectorNode",
        ("Integer", "Vector") : "an_CombineVectorNode",
        ("Integer List", "Polygon Indices") : "an_CreatePolygonIndicesNode",
        ("Polygon Indices List", "Edge Indices List") : "an_EdgesOfPolygonsNode",
        ("Vector List", "Mesh Data") : "an_CombineMeshDataNode",
        ("Mesh Data", "Vector List") : "an_SeparateMeshDataNode",
        ("Mesh Data", "BMesh") : "an_CreateBMeshFromMeshData",
        ("Particle System", "Particle List") : "an_GetParticlesNode",
        ("Integer", "Euler") : "an_CombineEulerNode",
        ("Float", "Euler") : "an_CombineEulerNode",
        ("Euler", "Float") : "an_SeparateEulerNode",
        ("Object", "Vector") : "an_ObjectTransformsInputNode",
        ("Object", "Matrix") : "an_ObjectMatrixInputNode"
    }

    def check(self, origin, target):
        return (origin.dataType, target.dataType) in self.rules
    def insert(self, nodeTree, origin, target, dataOrigin):
        nodeIdName = self.rules[(dataOrigin.dataType, target.dataType)]
        node = insertLinkedNode(nodeTree, nodeIdName, origin, target)

class ConvertVectorToEuler(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Vector" and target.dataType == "Euler"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertVectorAndEulerNode", origin, target)
        node.conversionType = "VECTOR_TO_EULER"
        node.inputs[0].linkWith(origin)
        node.outputs[0].linkWith(target)

class ConvertEulerToVector(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Euler" and target.dataType == "Vector"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertVectorAndEulerNode", origin, target)
        node.conversionType = "EULER_TO_VECTOR"
        node.inputs[0].linkWith(origin)
        node.outputs[0].linkWith(target)

class ConvertEulerToQuaternion(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Euler" and target.dataType == "Quaternion"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertRotationsNode", origin, target)
        node.conversionType = "EULER_TO_QUATERNION"
        node.inputs[0].linkWith(origin)
        node.outputs[0].linkWith(target)

class ConvertQuaternionToEuler(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Quaternion" and target.dataType == "Euler"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertRotationsNode", origin, target)
        node.conversionType = "QUATERNION_TO_EULER"
        node.inputs[0].linkWith(origin)
        node.outputs[0].linkWith(target)

class ConvertListToElement(LinkCorrection):
    def check(self, origin, target):
        return toBaseIdName(origin.bl_idname) == target.bl_idname
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertNode(nodeTree, "an_GetListElementNode", origin, target)
        node.assignType(target.dataType)
        insertBasicLinking(nodeTree, origin, node, target)

class ConvertElementToList(LinkCorrection):
    def check(self, origin, target):
        return origin.bl_idname == toBaseIdName(target.bl_idname)
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertNode(nodeTree, "an_CreateListNode", origin, target)
        node.assignBaseDataType(origin.dataType, inputAmount = 1)
        insertBasicLinking(nodeTree, origin, node, target)


class ConvertSeparatedMeshDataToBMesh(LinkCorrection):
    separatedMeshDataTypes = ["Vector List", "Edge Indices List", "Polygon Indices List"]
    def check(self, origin, target):
        return origin.dataType in self.separatedMeshDataTypes and target.dataType == "BMesh"
    def insert(self, nodeTree, origin, target, dataOrigin):
        toMeshData, toMesh = insertNodes(nodeTree, ["an_CombineMeshDataNode", "an_CreateBMeshFromMeshData"], origin, target)
        nodeTree.links.new(toMeshData.inputs[self.separatedMeshDataTypes.index(origin.dataType)], origin)
        nodeTree.links.new(toMesh.inputs[0], toMeshData.outputs[0])
        nodeTree.links.new(toMesh.outputs[0], target)

class ConvertListToLength(LinkCorrection):
    def check(self, origin, target):
        return "List" in origin.dataType and target.dataType == "Integer"
    def insert(self, nodeTree, origin, target, dataOrigin):
        insertLinkedNode(nodeTree, "an_GetListLengthNode", origin, target)

class ConvertToString(LinkCorrection):
    def check(self, origin, target):
        return target.dataType == "String"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertToStringNode", origin, target)

class ConvertFromGenericList(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Generic List" and isList(target.dataType)
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertNode", origin, target)

class ConvertFromGeneric(LinkCorrection):
    def check(self, origin, target):
        return origin.dataType == "Generic"
    def insert(self, nodeTree, origin, target, dataOrigin):
        node = insertLinkedNode(nodeTree, "an_ConvertNode", origin, target)
        tree_info.update()
        node.assignType(target.dataType)


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
        node.parent = leftSocket.node.parent
        nodes.append(node)
    return nodes

def insertBasicLinking(nodeTree, originSocket, node, targetSocket):
    nodeTree.links.new(node.inputs[0], originSocket)
    nodeTree.links.new(targetSocket, node.outputs[0])

def getSocketCenter(socket1, socket2):
    return (socket1.node.viewLocation + socket2.node.viewLocation) / 2

linkCorrectors = [
    ConvertSeparatedMeshDataToBMesh(),
    ConvertVectorToEuler(),
    ConvertEulerToVector(),
    ConvertEulerToQuaternion(),
    ConvertQuaternionToEuler(),
    ConvertListToElement(),
    ConvertElementToList(),
	ConvertListToLength(),
    SimpleConvert(),
    ConvertToString(),
    ConvertFromGenericList(),
    ConvertFromGeneric() ]
