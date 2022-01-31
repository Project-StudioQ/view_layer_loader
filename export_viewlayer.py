#
# ViewLayer Saver / コマンドラインからテンポラリにファイルを出力させる
#

import bpy
import sys

def main( ):
    try:
        bpy.ops.qcommon.save_load_workspace_save( )
    except:
        sys.exit( 1 )

    sys.exit( 0 )

if __name__ == "__main__":
    main( )

