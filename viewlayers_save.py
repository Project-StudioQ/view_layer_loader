import bpy
from .util import *

# -----------------------------------------------------------------------------

def search_view_layers( ):
    view_layer_settings = {}
    for vl in bpy.context.scene.view_layers:
        view_layer_settings[vl.name] = _search_in_layer_collection( vl.layer_collection )

    node_settings = []
    if bpy.context.scene.node_tree is not None:
        for node in bpy.context.scene.node_tree.nodes:
            # ID Mask -> Multiplyの連結ノードの時
            if isinstance( node, bpy.types.CompositorNodeIDMask ):
                result = _search_in_node_mask_id( node )
                if result:
                    node_settings.append( result )

    # 複数レンダーエンジンの対応用
    render_engines = {}
    for vl in bpy.context.scene.view_layers:
        if not hasattr(vl, "render_manager_item"):
            continue
        render_engines[vl.name] = vl.render_manager_item.render_engine

    json_data = {
        "version":VIEW_LAYER_SAVER_VERSION
    ,   "view_layers":view_layer_settings
    ,   "nodes": node_settings
    ,   "render_engines": render_engines
    }

    return json_data

# -----------------------------------------------------------------------------

def _search_in_layer_collection( lc ):
    c = lc.collection
    node = {
        "name": lc.name
    ,   "view_layer": {
            "exclude": lc.exclude
        ,   "hide_viewport": lc.hide_viewport
        ,   "holdout": lc.holdout
        ,   "indirect_only": lc.indirect_only
        }
    ,   "collection": {
            "hide_render": c.hide_render
        ,   "hide_select": c.hide_select
        ,   "hide_viewport": c.hide_viewport
        }
    }

    node["children"] = []
    for t in lc.children:
        node["children"].append( _search_in_layer_collection( t ) )

    return node

def _search_in_node_mask_id( node ):
    output_id = 0
    for t in node.outputs:
        output_node = node.output_template( output_id )

        if (
            output_node.identifier.lower( ) == "alpha"
        and t.enabled
        and t.is_output
        and 0 < len( t.links )
        and isinstance( t.links[0].to_node, bpy.types.CompositorNodeMath )
        and t.links[0].to_node.operation == 'MULTIPLY'
        ):
            value = None
            to_node = t.links[0].to_node
            for v in to_node.inputs:
                if len( v.links ) == 0:
                    value = v.default_value
                    break

            if value is not None:
                return {
                    "type": "ID_MASK_AND_MULTIPLY"
                ,   "id_mask": node.name
                ,   "math": to_node.name
                ,   "index": node.index
                ,   "value": value
                }
        output_id += 1

    return None
