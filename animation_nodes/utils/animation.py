from . blender_ui import iterActiveScreens

def isAnimationPlaying():
    return any([screen.is_animation_playing for screen in iterActiveScreens()])

def isAnimated(idObject):
    if not idObject:
        return False
    
    animationData = idObject.animation_data
    if not animationData:
        return False
    
    if animationData.action and len(animationData.action.fcurves) != 0:
        return True

    return len(animationData.drivers) != 0 or len(animationData.nla_tracks) != 0
