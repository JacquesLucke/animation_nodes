import bpy

class NodeCreator:
    def __init__(self, *args, **kwargs):
        self.nodesToMove = []
        self.insert(*args, **kwargs)
        self.moveInsertedNodes()

    def insert(self, *args, **kwargs):
        pass

    def take(self, node):
        self.nodesToMove.append(node)

    def newNode(self, type, x = 0, y = 0, move = True):
        bpy.ops.node.add_and_link_node(type = type)
        node = self.nodeTree.nodes[-1]
        node.location.x += x
        node.location.y += y
        if move: self.nodesToMove.append(node)
        return node

    def moveInsertedNodes(self):
        for node in self.nodeTree.nodes:
            node.select = node in self.nodesToMove
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

    @property
    def nodeTree(self):
        return bpy.context.space_data.edit_tree

    @property
    def activeNode(self):
        return getattr(bpy.context, "active_node", None)
