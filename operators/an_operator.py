class AnimationNodeOperator:
    @classmethod
    def poll(cls, context):
        return getattr(context.active_node, "isAnimationNode", False)
