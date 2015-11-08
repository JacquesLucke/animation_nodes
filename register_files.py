import bpy

from . import utils
from . import keymap
from . import events
from . import id_keys
from . import tree_info
from . import draw_handler
from . ui import node_colors
from . utils import selection
from . nodes.system import script
from . ui import generic_node_panel
from . ui import auto_nodetree_selection
from . operators import dynamic_operators
from . base_types import node as node_base
from . nodes.sound import bake as sound_bake
from . base_types import socket as socket_base
from . ui.node_menu import registerMenu, unregisterMenu

def registerFiles():
    id_keys.register()
    sound_bake.register()
    socket_base.register()
    node_colors.register()
    draw_handler.register()
    events.registerHandlers()
    script.registerHandlers()
    utils.operators.register()
    tree_info.registerHandlers()
    node_base.registerHandlers()
    selection.registerHandlers()
    generic_node_panel.register()
    dynamic_operators.registerHandlers()
    auto_nodetree_selection.registerHandlers()

    registerMenu()
    keymap.register()

def unregisterFiles():
    id_keys.unregister()
    sound_bake.unregister()
    socket_base.unregister()
    node_colors.unregister()
    draw_handler.unregister()
    events.unregisterHandlers()
    script.unregisterHandlers()
    utils.operators.unregister()
    tree_info.unregisterHandlers()
    node_base.unregisterHandlers()
    selection.unregisterHandlers()
    generic_node_panel.unregister()
    dynamic_operators.unregisterHandlers()
    auto_nodetree_selection.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()
