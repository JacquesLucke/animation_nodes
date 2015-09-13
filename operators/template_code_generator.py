import bpy
from .. utils.names import toVariableName
from .. execution.node_sorting import sortNodes

class TemplateCodeGenerator(bpy.types.Operator):
    bl_idname = "an.generator_template_code"
    bl_label = "Generate Template Code"

    def execute(self, context):
        tree = context.space_data.node_tree
        lines = list(self.iterCodeLines(tree))
        code = "\n".join(lines)
        self.outputCode(code)
        return {"FINISHED"}

    def iterCodeLines(self, tree):
        nodeNames = {}
        for node in self.sortNodes(tree.nodes):
            yield from iterNodeCreationLines(node, nodeNames)
        for link in tree.links:
            fromText = "{}.outputs[{}]".format(nodeNames[link.from_node], list(link.from_node.outputs).index(link.from_socket))
            toText = "{}.inputs[{}]".format(nodeNames[link.to_node], list(link.to_node.inputs).index(link.to_socket))
            yield "self.newLink({}, {})".format(fromText, toText)

    def sortNodes(self, nodes):
        animationNodes = [node for node in nodes if hasattr(node, "isAnimationNode")]
        otherNodes = [node for node in nodes if not hasattr(node, "isAnimationNode")]
        sortedAnimationNodes = sortNodes(animationNodes)
        return sortedAnimationNodes + otherNodes


    def outputCode(self, code):
        textBlock = bpy.data.texts.get("Template Code")
        if textBlock is None:
            textBlock = bpy.data.texts.new("Template Code")
        textBlock.from_string(code)

def iterNodeCreationLines(node, nodeNames):
    name = toVariableName(node.name)
    nodeNames[node] = name
    labelText = ", label = " + repr(node.label) if node.label else ""
    parameterText = "'{}', x = {:.0f}, y = {:.0f}{}".format(node.bl_idname, node.location.x, node.location.y, labelText)
    yield "{} = self.newNode({})".format(name, parameterText)
