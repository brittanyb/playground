import PySide6.QtCore as QtCore
import PySide6.QtWidgets as QtWidgets

from connection_widget import ConnectionWidget
from event_info import WidgetMessage, DataProcessMessage
from gui_handlers import GUIHandlers
from pad_model import PadEntry
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class DataReceiveSignaller(QtWidgets.QWidget):
    """Signal to emit when GUI event loop receives data from Data process."""

    ALL_PADS = QtCore.Signal(list)
    PROFILE_NAMES = QtCore.Signal(list)
    PAD_CONNECTED = QtCore.Signal(bool)
    FRAME_DATA = QtCore.Signal(PadEntry)
    PROFILE_NEW = QtCore.Signal(str)
    PROFILE_SAVED = QtCore.Signal(bool)
    PROFILE_LOADED = QtCore.Signal(str)
    PROFILE_RENAMED = QtCore.Signal(tuple)
    PROFILE_REMOVED = QtCore.Signal(bool)

    def __init__(self):
        super(DataReceiveSignaller, self).__init__()


class Widgets:
    def __init__(self):
        self.connection_widget = ConnectionWidget()
        self.pad_widget = PadWidget()
        self.profile_widget = ProfileWidget()
        self.signals = DataReceiveSignaller()
        self.handlers = GUIHandlers(
            self.connection_widget, self.pad_widget, self.profile_widget
        )

        self.hooks = {
            self.connection_widget.CONNECT_CLICKED: WidgetMessage.CONNECT,
            self.connection_widget.REFRESH_CLICKED: WidgetMessage.REFRESH,
            self.pad_widget.FRAME_READY: WidgetMessage.FRAME_READY,
            self.pad_widget.NEW_SENS_VALUE: WidgetMessage.SENSOR_UPDATE,
            self.profile_widget.NEW_CLICKED: WidgetMessage.NEW,
            self.profile_widget.SAVE_CLICKED: WidgetMessage.SAVE,
            self.profile_widget.REMOVE_CLICKED: WidgetMessage.REMOVE,
            self.profile_widget.RENAME_CLICKED: WidgetMessage.RENAME,
            self.profile_widget.DROPDOWN_ACTIVATED: WidgetMessage.SELECT
        }

        self.data_requests = {
            WidgetMessage.INIT: [],
            WidgetMessage.CONNECT: [self.connection_widget.get_pad_serial],
            WidgetMessage.REFRESH: [],
            WidgetMessage.QUIT: [],
            WidgetMessage.FRAME_READY: [],
            WidgetMessage.SENSOR_UPDATE: [self.pad_widget.get_update_data],
            WidgetMessage.NEW: [],
            WidgetMessage.SAVE: [self.profile_widget.get_pad_name],
            WidgetMessage.REMOVE: [self.profile_widget.get_pad_name],
            WidgetMessage.RENAME: [
                self.profile_widget.get_pad_name,
                self.profile_widget.get_profile_name
            ],
            WidgetMessage.SELECT: [self.profile_widget.get_pad_name]
        }

        self.process_requests = {
            DataProcessMessage.ALL_PADS: self.signals.ALL_PADS,
            DataProcessMessage.PROFILE_NAMES: self.signals.PROFILE_NAMES,
            DataProcessMessage.PAD_CONNECTED: self.signals.PAD_CONNECTED,
            DataProcessMessage.FRAME_DATA: self.signals.FRAME_DATA,
            DataProcessMessage.PROFILE_SAVED: self.signals.PROFILE_SAVED,
            DataProcessMessage.PROFILE_LOADED: self.signals.PROFILE_LOADED,
            DataProcessMessage.PROFILE_NEW: self.signals.PROFILE_NEW,
            DataProcessMessage.PROFILE_RENAMED: self.signals.PROFILE_RENAMED,
            DataProcessMessage.PROFILE_REMOVED: self.signals.PROFILE_REMOVED
        }

        self.signal_handlers = {
            self.signals.ALL_PADS: self.handlers.all_pads_received,
            self.signals.PROFILE_NAMES: self.handlers.profile_names_received,
            self.signals.PAD_CONNECTED: self.handlers.pad_connected,
            self.signals.FRAME_DATA: self.handlers.frame_data_received,
            self.signals.PROFILE_SAVED: self.handlers.profile_saved,
            self.signals.PROFILE_LOADED: self.handlers.profile_loaded,
            self.signals.PROFILE_RENAMED: self.handlers.profile_renamed,
            self.signals.PROFILE_NEW: self.handlers.profile_new,
            self.signals.PROFILE_REMOVED: self.handlers.profile_removed
        }
