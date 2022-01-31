import bpy
import json
import os
import subprocess
from bpy.props import BoolProperty, EnumProperty, PointerProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from .viewlayers_load import load_view_layers
from .viewlayers_save import search_view_layers
from .util import *

# -----------------------------------------------------------------------------

class QCOMMON_OT_SAVE_save_load_view_layers(bpy.types.PropertyGroup):
    blend_path: StringProperty()
    mode: EnumProperty(
        items=[
            (MODE_NONE, "曖昧一致", "末尾が一致しているものは設定"),
            (MODE_COMPLETE, "完全一致", "名前が完全に一致しているものは設定"),
            (MODE_MERGE, "同一合成", "同一アセットを合成"),
            (MODE_SEPARATE, "同一分離", "同一アセットを分離")
        ],
        default=MODE_NONE
    )
    add_view_layer_name: StringProperty()
    copy_currently_view_layer: BoolProperty(default=True)

# -----------------------------------------------------------------------------

class QCOMMON_OT_save_load_view_layers_load(bpy.types.Operator):
    """
        view layer 状態読込の実行
    """
    bl_label = "Save Workspace Status"
    bl_idname = "qcommon.save_load_workspace_load"
    bl_description = "Save workspace status"
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定

    def execute(self, context):
        props = context.scene.temp_view_layer_saveload

        try:
            os.remove( VIEW_LAYER_SAVER_TEMP_FILE )
        except:
            pass

        script_path = os.path.join(os.path.dirname(__file__), "export_viewlayer.py")
        result = subprocess.run([
            bpy.app.binary_path
        ,   "-b"
        ,   props.blend_path
        ,   "-P"
        ,   script_path
        ])
        if result.returncode != 0:
            self.report({'ERROR'}, "Crash Blender when save ViewLayer to temporary directory.")
            return {'CANCELLED'}

        try:
            with open( VIEW_LAYER_SAVER_TEMP_FILE, 'r' ) as f:
                json_data = json.load( f )
        except:
            self.report({'ERROR'}, f"Can't load ViewLayer from {props.blend_path}")
            return {'CANCELLED'}

        load_view_layers( json_data )

        return{'FINISHED'}

class QCOMMON_OT_save_load_view_layers_save(bpy.types.Operator):
    """
        view layer 状態保存の実行
    """
    bl_label = "Save Workspace Status"
    bl_idname = "qcommon.save_load_workspace_save"
    bl_description = "Save workspace status"
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定

    def execute(self, context):
        props = context.scene.temp_view_layer_saveload
        json_data = search_view_layers()

        try:
            with open( VIEW_LAYER_SAVER_TEMP_FILE, 'w' ) as f:
                json.dump( json_data, f )
        except:
            self.report({'ERROR'}, f"Can't save view layer json to {props.json_data}.")
            return {'CANCELLED'}

        return{'FINISHED'}

class QCOMMON_OT_save_load_view_layers_select_blend_path(bpy.types.Operator, ImportHelper):
    bl_idname = "qcommon.save_load_view_layers_select_blend_path"
    bl_label = "Select Blend Path"
    bl_description = "Import/Export a .blend file"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(
        default="*.blend",
        options={'HIDDEN'},
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = context.scene.temp_view_layer_saveload
        props.blend_path = self.filepath
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}

class QCOMMON_PT_save_load_view_layers(bpy.types.Panel):
    """
        UI表示処理
    """
    bl_label = "View Layer Loader"
    bl_idname = "QCOMMON_PT_save_load_view_layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Q_COMMON"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        props = context.scene.temp_view_layer_saveload
        layout = self.layout

        row = layout.row()
        row.prop(props, "blend_path", text="Blend Path")
        row.operator(QCOMMON_OT_save_load_view_layers_select_blend_path.bl_idname, text='',icon='FILE_FOLDER')

        row = layout.row(align=True)
        row.prop( props, "mode", expand=True)
        col = layout.column(align=True)
        if props.mode != MODE_NONE:
            col.prop( props, "copy_currently_view_layer", text="不一致は現在のレイヤー設定をコピー" )
        col.prop( props, "add_view_layer_name", text="ViewLayerに追加する文字" )
        layout.operator( QCOMMON_OT_save_load_view_layers_load.bl_idname, text="Load" )

# -----------------------------------------------------------------------------

classes = (
    QCOMMON_OT_SAVE_save_load_view_layers,
    QCOMMON_OT_save_load_view_layers_load,
    QCOMMON_OT_save_load_view_layers_save,
    QCOMMON_OT_save_load_view_layers_select_blend_path,
    QCOMMON_PT_save_load_view_layers,
)

def register():
    """
        クラス登録
    """
    for i in classes:
        bpy.utils.register_class(i)

    _initialized( )

def unregister():
    """
        クラス登録解除
    """

    for i in classes:
        bpy.utils.unregister_class(i)

    _deinitialized( )

def _initialized( ):
    bpy.types.Scene.temp_view_layer_saveload = PointerProperty(type=QCOMMON_OT_SAVE_save_load_view_layers)

def _deinitialized( ):
    del bpy.types.Scene.temp_view_layer_saveload
