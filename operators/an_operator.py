class AnimationNodeOperator:
    @classmethod
    def poll(cls, context):
        node = context.active_node
        return hasattr(node, "isAnimationNode")
