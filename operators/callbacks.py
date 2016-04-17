from .. utils.names import getRandomString
from .. utils.nodes import idToNode, idToSocket

callbackByIdentifier = {}

def newCallback(function):
    identifier = getRandomString(10)
    callbackByIdentifier[identifier] = function
    return identifier

def executeCallback(identifier, *args, **kwargs):
    if identifier == "":
        return

    callback = callbackByIdentifier[identifier]
    callback(*args, **kwargs)


# Callback Utils
########################################

def newNodeCallback(node, functionName):
    callback = createNodeCaller(node.toID(), functionName)
    return newCallback(callback)

def createNodeCaller(nodeID, functionName):
    def callback(*args, **kwargs):
        node = idToNode(nodeID)
        function = getattr(node, functionName)
        function(*args, **kwargs)
    return callback


def newSocketCallback(socket, functionName):
    callback = createSocketCaller(socket.toID(), functionName)
    return newCallback(callback)

def createSocketCaller(socketID, functionName):
    def callback(*args, **kwargs):
        socket = idToSocket(socketID)
        function = getattr(socket, functionName)
        function(*args, **kwargs)
    return callback
