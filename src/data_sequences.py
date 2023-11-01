from event_info import DataProcessMessage, WidgetMessage
from pad_model import PadModel
from profile_controller import ProfileController
from reflex_controller import ReflexController


class Sequences:
    pad_controller = ReflexController()
    pad_model = PadModel()
    profile_controller = ProfileController(pad_model)

    receive = {
        WidgetMessage.INIT: [
            pad_controller.get_all_pads,
            profile_controller.initialise_profile,
            pad_model.get_model_data
        ],
        WidgetMessage.FRAME_READY: [
            pad_model.get_model_data
        ],
        WidgetMessage.CONNECT: [
            pad_controller.toggle_pad_connection
        ],
        WidgetMessage.REFRESH: [
            pad_controller.enumerate_pads,
            pad_controller.get_all_pads
        ],
        WidgetMessage.QUIT: [
            pad_controller.disconnect_pad
        ],
        WidgetMessage.SENSOR_UPDATE: [
            pad_model.set_sensor
        ],
        WidgetMessage.NEW: [
            pad_model.set_default,
            profile_controller.create_new_profile
        ],
        WidgetMessage.SAVE: [
            profile_controller.save_user_profile
        ],
        WidgetMessage.SELECT: [
            profile_controller.load_user_profile
        ],
        WidgetMessage.RENAME: [
            profile_controller.rename_user_profile
        ],
        WidgetMessage.REMOVE: [
            profile_controller.remove_user_profile
        ]
    }

    transmit = {
        pad_controller.get_all_pads:
            DataProcessMessage.ALL_PADS,
        profile_controller.initialise_profile:
            DataProcessMessage.PROFILE_NAMES,
        pad_controller.toggle_pad_connection:
            DataProcessMessage.PAD_CONNECTED,
        pad_model.get_model_data:
            DataProcessMessage.FRAME_DATA,
        profile_controller.create_new_profile:
            DataProcessMessage.PROFILE_NEW,
        profile_controller.save_user_profile:
            DataProcessMessage.PROFILE_SAVED,
        profile_controller.load_user_profile:
            DataProcessMessage.PROFILE_LOADED,
        profile_controller.rename_user_profile:
            DataProcessMessage.PROFILE_RENAMED,
        profile_controller.remove_user_profile:
            DataProcessMessage.PROFILE_REMOVED
    }

    def handle_sensor_data(self):
        if not (pad := self.pad_controller.pad):
            return
        pad.handle_sensor_data()

    def handle_light_data(self):
        if not (pad := self.pad_controller.pad):
            return
        pad.handle_light_data()
