import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore

from pad_model import PadEntry


class WidgetMessage:
    """Message string to pass over queue from Widget event to Data process."""

    REFRESH = "GUI_refresh_pads"
    CONNECT = "GUI_connect_pad"
    NEW = "GUI_new_profile"
    REMOVE = "GUI_remove_profile"
    RENAME = "GUI_rename_profile"
    SAVE = "GUI_save_profile"
    SELECT = "GUI_select_profile"
    INIT = "GUI_init_window"
    QUIT = "GUI_quit"
    FRAME_READY = "GUI_frame_ready"


class DataProcessMessage:
    """Message string to pass over queue from Data process event to Widget."""

    ALL_PADS = "DP_all_pads"
    PROFILE_NAMES = "DP_profile_names"
    PAD_CONNECTED = "DP_pad_connected"
    FRAME_DATA = "DP_frame_data"


class DataReceiveSignaller(QtWidgets.QWidget):
    """Signal to emit when GUI event loop receives data from Data process."""

    ALL_PADS = QtCore.Signal(list)
    PROFILE_NAMES = QtCore.Signal(list)
    PAD_CONNECTED = QtCore.Signal(bool)
    FRAME_DATA = QtCore.Signal(PadEntry)

    def __init__(self):
        super(DataReceiveSignaller, self).__init__()
