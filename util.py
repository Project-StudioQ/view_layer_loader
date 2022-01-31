import os
import tempfile

VIEW_LAYER_SAVER_VERSION = 1004
VIEW_LAYER_SAVER_TEMP_FILE = os.path.join( tempfile.gettempdir( ), "viewlayer_save.json" )

MODE_NONE = "NONE"
MODE_COMPLETE = "COMPLETE"
MODE_MERGE = "MERGE"
MODE_SEPARATE = "SEPARATE"
