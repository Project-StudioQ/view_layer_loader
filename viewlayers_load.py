import bpy
from collections import deque
from .util import *

# -----------------------------------------------------------------------------

DATA_BLOCK_TEXT = "/Text/"
DEFAULT_VIEW_LAYER = "View Layer"
DEFAULT_VIEW_LAYER_VER3 = "ViewLayer"

# -----------------------------------------------------------------------------

def load_view_layers( json_data ):
    props = bpy.context.scene.temp_view_layer_saveload

    # 先に存在しないView Layerを生成する
    view_layer_settings = json_data["view_layers"]
    for name in view_layer_settings.keys( ):
        vl_name = _calc_view_layer_name( name )
        if vl_name not in bpy.context.scene.view_layers:
            vl = bpy.context.scene.view_layers.new( vl_name )

    # 各々のView Layerの設定を復元
    applied_objects = {}
    for name in view_layer_settings.keys( ):
        node = view_layer_settings[name]
        vl_name = _calc_view_layer_name( name )
        vl = bpy.context.scene.view_layers[vl_name]
        if ( hasattr( props, "mode" ) and props.mode != "NONE"):
            if hasattr( props, "copy_currently_view_layer" ) and props.copy_currently_view_layer:
                if bpy.context.view_layer != vl:
                    print( bpy.context.view_layer.name, " -> ", vl.name )
                    _set_default_currently_view_layers( bpy.context.view_layer.layer_collection, vl.layer_collection, applied_objects )
        _set_view_layer( vl.layer_collection, node, applied_objects )

    # node 設定
    if bpy.context.scene.use_nodes:
        node_settings = json_data["nodes"]
        for ns in node_settings:
            if ns["type"] == "ID_MASK_AND_MULTIPLY":
                _node_set_mask_and_multiply( ns )
                
    # 複数レンダーエンジンの設定(Q独自)
    render_engines = json_data["render_engines"]
    for key in render_engines.keys():
        vl_name = _calc_view_layer_name( key )
        if vl_name not in bpy.context.scene.view_layers:
            continue
        vl = bpy.context.scene.view_layers[vl_name]
        vl.render_manager_item.render_engine = render_engines[key]

# -----------------------------------------------------------------------------

def _set_view_layer( lc, node, applied_objects ):
    find_master = False
    for c in node["children"]:
        if 0 < len( c["children"] ) and ( not c["name"].endswith("_tmp") ):
            find_master = True
            node_chara_name = c["name"]
            _new_set_in_layer_collection( lc, c, node_chara_name, applied_objects )

    if not find_master:
        # 古い設定方法を使う
        print( "WARNING: Use OLD method for non-standard layer structures.")
        _old_set_in_layer_collection( lc, node )

def _set_default_currently_view_layers( src_lc, dest_lc, applied_objects ):
    """
        設定のないものを現在のViewLayerからコピーする
    """
    if src_lc.name not in applied_objects:
        src_c = src_lc.collection
        dest_c = dest_lc.collection

        dest_lc.exclude = src_lc.exclude
        dest_lc.hide_viewport = src_lc.hide_viewport
        dest_lc.holdout = src_lc.holdout
        dest_lc.indirect_only = src_lc.indirect_only

        dest_c.hide_render = src_c.hide_render
        dest_c.hide_select = src_c.hide_select
        dest_c.hide_viewport = src_c.hide_viewport

    for t in src_lc.children:
        if t.name in dest_lc.children:
            _set_default_currently_view_layers( t, dest_lc.children[t.name], applied_objects )

def _new_set_in_layer_collection( layer_collection, node, node_chara_name, applied_objects ):
    def check_lc( lc, lc_chara_name, filter_collections ):
        lc_name = lc.name
        props = bpy.context.scene.temp_view_layer_saveload

        # 名前完全一致モード
        if hasattr( props, "mode" ) and props.mode == MODE_COMPLETE:
            if lc_name != node["name"]:
                return
        # 同一アセット合成モード
        elif hasattr( props, "mode" ) and props.mode == MODE_MERGE:
            lc_name = lc_name.split(".")[0]
            if lc_name != node["name"].split(".")[0]:
                return
        # 同一アセット分離モード
        elif hasattr( props, "mode" ) and props.mode == MODE_SEPARATE:
            if lc_name not in filter_collections:
                return
            lc_name = lc_name.split(".")[0]
            if lc_name != node["name"].split(".")[0]:
                return
        else:
            lc_name = lc_name.split(".")[0]
            if lc_name[len(lc_chara_name)+1:] != node["name"][len(node_chara_name)+1:]:
                return
        print( "COPY to %s -> %s" % ( node["name"], lc.name ))
        c = lc.collection

        node_vc = node["view_layer"]
        lc.exclude = node_vc["exclude"]
        lc.hide_viewport = node_vc["hide_viewport"]
        lc.holdout = node_vc["holdout"]
        lc.indirect_only = node_vc["indirect_only"]

        node_c = node["collection"]
        c.hide_render = node_c["hide_render"]
        c.hide_select = node_c["hide_select"]
        c.hide_viewport = node_c["hide_viewport"]

        applied_objects[lc.name] = True

    def recur_lc( lc, lc_chara_name ):
        props = bpy.context.scene.temp_view_layer_saveload
        
        needs_to_update = False
        if lc_chara_name is None:
            needs_to_update = True
            lc_chara_name = ""

        filter_collections = None
        if props.mode == MODE_MERGE or props.mode == MODE_SEPARATE:
            filter_lc = bpy.context.scene.collection.children[props.add_view_layer_name]
            filter_collections = get_layer_collection_all( filter_lc )

        check_lc( lc, lc_chara_name, filter_collections )
        for c in lc.children:
            if needs_to_update:
                lc_chara_name = c.name
                if hasattr( props, "mode" ) and props.mode == MODE_COMPLETE:
                    pass
                else:
                    lc_chara_name = lc_chara_name.split(".")[0]
            recur_lc( c, lc_chara_name )

    def get_layer_collection_all( lc ):
        layer_collections = list( [c.name for c in lc.children] )
        collections = deque( list( lc.children ) )
        while( len( collections ) > 0 ):
            child = collections.popleft( )
            for c in child.children:
                layer_collections.append( c.name )
                collections.append( c )
        return layer_collections

    recur_lc( layer_collection, None )

    for t in node["children"]:
        _new_set_in_layer_collection( layer_collection, t, node_chara_name, applied_objects )

def _old_set_in_layer_collection( lc, node ):
    c = lc.collection

    if lc.name != node["name"]:
        print( "Warning: %s does not match with node name (%s)." % ( lc.name, node["name"] ) )

    node_vc = node["view_layer"]
    lc.exclude = node_vc["exclude"]
    lc.hide_viewport = node_vc["hide_viewport"]
    lc.holdout = node_vc["holdout"]
    lc.indirect_only = node_vc["indirect_only"]

    node_c = node["collection"]
    c.hide_render = node_c["hide_render"]
    c.hide_select = node_c["hide_select"]
    c.hide_viewport = node_c["hide_viewport"]

    for t in node["children"]:
        if t["name"] in lc.children:
            _old_set_in_layer_collection( lc.children[t["name"]], t )

def _node_set_mask_and_multiply( ns ):
    for node in bpy.context.scene.node_tree.nodes:
        if isinstance( node, bpy.types.CompositorNodeIDMask ) and node.index == ns["index"]:
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
                    to_node = t.links[0].to_node
                    for v in to_node.inputs:
                        if len( v.links ) == 0:
                            v.default_value = ns["value"]
                            return
                output_id += 1

def _calc_view_layer_name( view_layer_name ):
    """ プロパティを元にViewLayer名を取得

    Args:
        view_layer_name (string): 元ViewLayer名

    Returns:
        string: ViewLayer名
    """
    props = bpy.context.scene.temp_view_layer_saveload
    if view_layer_name == _get_default_view_layer_name() or props.add_view_layer_name == "":
        return view_layer_name
    else:
        return props.add_view_layer_name + "_" + view_layer_name
    
def _get_default_view_layer_name( ):
    """ Verに応じてデフォルトのViewLayerの名前を取得

    Returns:
        str: デフォルトのViewLayerの名前
    """
    # 3.0以下は「View Layer」
    if bpy.app.version < ( 3, 0, 0 ):
        return DEFAULT_VIEW_LAYER
    # 3.0で「ViewLayer」に
    else:
        return DEFAULT_VIEW_LAYER_VER3