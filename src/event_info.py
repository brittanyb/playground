import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore


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


class DataProcessMessage:
    """Message string to pass over queue from Data process event to Widget."""

    ALL_PADS = "DP_all_pads"
    PROFILE_NAMES = "DP_profile_names"
    PAD_CONNECTED = "DP_pad_connected"


class DataReceiveSignaller(QtWidgets.QWidget):
    """Signal to emit when GUI event loop receives data from Data process."""

    ALL_PADS = QtCore.Signal(list)
    PROFILE_NAMES = QtCore.Signal(list)
    PAD_CONNECTED = QtCore.Signal(bool)

    def __init__(self):
        super(DataReceiveSignaller, self).__init__()
