from connection_widget import ConnectionWidget
from pad_model import PadEntry
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class GUIHandlers:
    """Methods to run on widgets on data process requests."""

    def __init__(
        self, connection_widget: ConnectionWidget, pad_widget: PadWidget,
        profile_widget: ProfileWidget
    ):
        self._connection_widget = connection_widget
        self._pad_widget = pad_widget
        self._profile_widget = profile_widget
        self._initialise_widgets()

    def _initialise_widgets(self) -> None:
        self._connection_widget.set_dropdown_state(False)
        self._connection_widget.set_connect_button_state(False)
        self._connection_widget.set_refresh_button_state(False)
        self._profile_widget.set_save_button(False)
        self._profile_widget.set_new_button(False)
        self._profile_widget.set_remove_button(False)
        self._profile_widget.set_rename_button(False)
        self._profile_widget.set_dropdown_state(False)

    def all_pads_received(self, all_pads: list[str]) -> None:
        pads_available = len(all_pads) > 0
        self._connection_widget.set_dropdown_state(pads_available)
        self._connection_widget.set_connect_button_state(pads_available)
        self._connection_widget.set_refresh_button_state(pads_available)
        self._connection_widget.set_dropdown_items(all_pads)

    def profile_names_received(self, profile_names: list[str]) -> None:
        self._profile_widget.set_dropdown_items(profile_names)
        self._profile_widget.set_dropdown_id(0)
        self._profile_set_widget_states()

    def pad_connected(self, connected: bool) -> None:
        self._connection_widget.set_dropdown_state(not connected)
        self._connection_widget.set_connect_button_icon(not connected)
        self._connection_widget.set_refresh_button_state(not connected)

    def frame_data_received(self, frame_data: PadEntry) -> None:
        if frame_data.updated:
            self._profile_widget.set_save_button(True)
        self._pad_widget.update(frame_data)

    def profile_saved(self, success: bool) -> None:
        self._profile_widget.set_save_button(not success)

    def profile_loaded(self, name: str) -> None:
        self._profile_widget.set_save_button(False)

    def profile_renamed(self, names: tuple[str, str]) -> None:
        self._profile_widget.rename_dropdown_item(names)
        self._profile_widget.set_save_button(False)

    def profile_new(self, name: str) -> None:
        if not self._profile_widget.get_num_dropdown_items() > 0:
            self._profile_widget.set_dropdown_items()
        self._profile_widget.add_dropdown_item(name)
        self._profile_widget.set_dropdown_by_text(name)
        self._profile_set_widget_states()

    def profile_removed(self, success: bool) -> None:
        if not success:
            return
        name = self._profile_widget.get_pad_name()
        self._profile_widget.remove_dropdown_item(name)
        self._profile_widget.set_dropdown_id(0)
        self._profile_set_widget_states()

    def _profile_set_widget_states(self) -> None:
        profiles_available = self._profile_widget.get_num_dropdown_items() > 1
        self._profile_widget.set_dropdown_state(profiles_available)
        self._profile_widget.set_remove_button(profiles_available)
        self._profile_widget.set_new_button(True)
        self._profile_widget.set_rename_button(True)
        self._profile_widget.set_save_button(False)
