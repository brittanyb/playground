import dataclasses

from event_info import DataProcessMessage, WidgetMessage
from led_data_handler import LEDDataHandler
from pad_model import PadModel
from profile_controller import ProfileController
from reflex_controller import ReflexController
from sensor_data_handler import SensorDataHandler


@dataclasses.dataclass
class Sequences:
    _pad_controller = ReflexController()
    _pad_model = PadModel()
    _profile_controller = ProfileController(_pad_model)
    _led_handler = LEDDataHandler()
    _sensor_handler = SensorDataHandler()

    receive = {
        WidgetMessage.INIT: [
            _pad_controller.get_all_pads,
            _profile_controller.initialise_profile,
            _pad_model.get_model_data
        ],
        WidgetMessage.FRAME_READY: [
            _pad_model.get_model_data
        ],
        WidgetMessage.CONNECT: [
            _pad_controller.toggle_pad_connection
        ],
        WidgetMessage.REFRESH: [
            _pad_controller.enumerate_pads,
            _pad_controller.get_all_pads
        ],
        WidgetMessage.QUIT: [
            _pad_controller.disconnect_pad
        ],
        WidgetMessage.SENSOR_UPDATE: [
            _pad_model.set_sensor
        ],
        WidgetMessage.NEW: [
            _pad_model.set_default,
            _profile_controller.create_new_profile
        ],
        WidgetMessage.SAVE: [
            _profile_controller.save_user_profile
        ],
        WidgetMessage.SELECT: [
            _profile_controller.load_user_profile
        ],
        WidgetMessage.RENAME: [
            _profile_controller.rename_user_profile
        ],
        WidgetMessage.REMOVE: [
            _profile_controller.remove_user_profile
        ]
    }

    transmit = {
        _pad_controller.get_all_pads:
            DataProcessMessage.ALL_PADS,
        _profile_controller.initialise_profile:
            DataProcessMessage.PROFILE_NAMES,
        _pad_controller.toggle_pad_connection:
            DataProcessMessage.PAD_CONNECTED,
        _pad_model.get_model_data:
            DataProcessMessage.FRAME_DATA,
        _profile_controller.create_new_profile:
            DataProcessMessage.PROFILE_NEW,
        _profile_controller.save_user_profile:
            DataProcessMessage.PROFILE_SAVED,
        _profile_controller.load_user_profile:
            DataProcessMessage.PROFILE_LOADED,
        _profile_controller.rename_user_profile:
            DataProcessMessage.PROFILE_RENAMED,
        _profile_controller.remove_user_profile:
            DataProcessMessage.PROFILE_REMOVED
    }
