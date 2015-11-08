import bpy

from . import utils
from . import keymap
from . import id_keys
from . import tree_info
from . import draw_handler
from . ui import node_colors
from . ui import generic_node_panel
from . ui import auto_nodetree_selection
from . operators import dynamic_operators
from . base_types import node as node_base
from . nodes.sound import bake as sound_bake
from . base_types import socket as socket_base
from . ui.node_menu import registerMenu, unregisterMenu

def registerFiles():
    id_keys.register()
    node_base.register()
    sound_bake.register()
    socket_base.register()
    node_colors.register()
    draw_handler.register()
    utils.operators.register()
    dynamic_operators.register()
    tree_info.registerHandlers()
    generic_node_panel.register()
    utils.handlers.registerHandlers()
    auto_nodetree_selection.registerHandlers()

    registerMenu()
    keymap.register()

def unregisterFiles():
    id_keys.unregister()
    node_base.unregister()
    sound_bake.unregister()
    socket_base.unregister()
    node_colors.unregister()
    draw_handler.unregister()
    utils.operators.unregister()
    dynamic_operators.unregister()
    tree_info.unregisterHandlers()
    generic_node_panel.unregister()
    utils.handlers.unregisterHandlers()
    auto_nodetree_selection.unregisterHandlers()

    unregisterMenu()
    keymap.unregister()
