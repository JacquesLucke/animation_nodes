from .. import tree_info
from . node import AnimationNode
from .. utils.handlers import eventHandler
from .. utils.nodes import iterAnimationNodes

class StaticAnimationNode(AnimationNode):
    def init(self, context):
        super().init(context)
        self.updateSockets()

    def updateSockets(self, context = None):
        @tree_info.keepNodeState
        def createSocketsWrapper(self):
            self.clearSockets()
            self.createSockets()

        tree_info.updateIfNecessary()
        createSocketsWrapper(self)

    def createSockets(self):
        raise NotImplementedError()


@eventHandler("FILE_LOAD_POST")
def updateSockets():
    idNames = [cls.bl_idname for cls in StaticAnimationNode.__subclasses__()]
    for node in iterAnimationNodes():
        if node.bl_idname in idNames:
            node.updateSockets()
