import bpy

class InsertNodesTemplate:
    def __init__(self, *args, **kwargs):
        self.nodes = []
        self.insert(*args, **kwargs)
        self.moveInsertedNodes()

    def insert(self, *args, **kwargs):
        pass

    def newNode(self, type, x = 0, y = 0):
        bpy.ops.node.add_and_link_node(type = type)
        node = self.nodeTree.nodes[-1]
        node.location.x += x
        node.location.y += y
        self.nodes.append(node)
        return node

    def moveInsertedNodes(self):
        for node in self.nodeTree.nodes:
            node.select = node in self.nodes
        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

    @property
    def nodeTree(self):
        return bpy.context.space_data.edit_tree
