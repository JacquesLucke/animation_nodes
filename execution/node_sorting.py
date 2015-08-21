from .. exceptions import NodeRecursionDetected

def sortNodes(nodes):
    """
    The nodes in the returned list can be executed successively.
    That means all dependencies are always before their target node.
    An exception is raised when the links are recursice.
    """
    preSort = []
    for node in nodes:
        preSort.extend(getAllDependencies(node))
        preSort.append(node)
    return removeDuplicates(preSort)

def removeDuplicates(elements):
    seen = set()
    see = seen.add
    return [element for element in elements if not(element in seen or see(element))]

def getAllDependencies(node, recursionStart = None):
    dependencies = []
    dataOrigins = node.originNodes
    for dataOrigin in dataOrigins:
        if dataOrigin == recursionStart: raise NodeRecursionDetected()
        dependencies.extend(getAllDependencies(dataOrigin, recursionStart = node))
    dependencies.extend(dataOrigins)
    return dependencies
