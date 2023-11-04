from event_info import DataProcessMessage, WidgetMessage
from pad_model import PadModel
from profile_controller import ProfileController
from reflex_controller import ReflexController


class Sequences:
    pad_controller = ReflexController()
    pad_model = PadModel()
    profile_controller = ProfileController(pad_model)
    _sensor_delta = None
    _light_delta = None

    receive = {
        WidgetMessage.CONNECT: [
            pad_controller.toggle_pad_connection
        ],
        WidgetMessage.FRAME_READY: [
            pad_model.get_model_data
        ],
        WidgetMessage.INIT: [
            pad_controller.get_all_pads,
            profile_controller.initialise_profile,
            pad_model.get_model_data
        ],
        WidgetMessage.NEW: [
            pad_model.set_default,
            profile_controller.create_new_profile
        ],
        WidgetMessage.QUIT: [
            pad_controller.disconnect_pad
        ],
        WidgetMessage.REFRESH: [
            pad_controller.enumerate_pads,
            pad_controller.get_all_pads
        ],
        WidgetMessage.SENSOR_UPDATE: [
            pad_model.set_sensor
        ],
        WidgetMessage.SAVE: [
            profile_controller.save_user_profile
        ],
        WidgetMessage.SELECT: [
            profile_controller.load_user_profile
        ],
        WidgetMessage.REMOVE: [
            profile_controller.remove_user_profile
        ],
        WidgetMessage.RENAME: [
            profile_controller.rename_user_profile
        ],
        WidgetMessage.VIEW_UPDATED: [
            pad_model.view_updated
        ]
    }

    transmit = {
        pad_controller.get_all_pads:
            DataProcessMessage.ALL_PADS,
        pad_controller.toggle_pad_connection:
            DataProcessMessage.PAD_CONNECTED,
        pad_model.get_model_data:
            DataProcessMessage.FRAME_DATA,
        pad_model.set_sensor:
            DataProcessMessage.SENSOR_UPDATED,
        profile_controller.create_new_profile:
            DataProcessMessage.PROFILE_NEW,
        profile_controller.load_user_profile:
            DataProcessMessage.PROFILE_LOADED,
        profile_controller.initialise_profile:
            DataProcessMessage.PROFILE_NAMES,
        profile_controller.remove_user_profile:
            DataProcessMessage.PROFILE_REMOVED,
        profile_controller.rename_user_profile:
            DataProcessMessage.PROFILE_RENAMED,
        profile_controller.save_user_profile:
            DataProcessMessage.PROFILE_SAVED,
    }

    def handle_pad_data(self):
        if not (pad := self.pad_controller.pad):
            return
        delta = pad.handle_sensor_data()
        if self._sensor_delta is None and delta:
            self._sensor_delta = delta
        delta = pad.handle_light_data()
        if self._light_delta is None and delta:
            self._light_delta = delta
        if self._sensor_delta and self._light_delta:
            print(f"{self._sensor_delta=:8.5f} {self._light_delta=:8.5f}")
            self._sensor_delta = None
            self._light_delta = None
