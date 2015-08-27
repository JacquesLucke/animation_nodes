from .. problems import NodeLinkRecursion

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
    if recursionStart is None: recursionStart = node
    dependencies = []
    dataOrigins = node.originNodes
    for dataOrigin in dataOrigins:
        if dataOrigin == recursionStart:
            NodeLinkRecursion().report()
            raise Exception()
        dependencies.extend(getAllDependencies(dataOrigin, recursionStart))
    dependencies.extend(dataOrigins)
    return dependencies
