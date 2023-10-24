from connection_widget import ConnectionWidget
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
        self.initialise_widgets()

    def initialise_widgets(self) -> None:
        self._connection_widget.set_dropdown_state(False)
        self._connection_widget.set_connect_button_state(False)
        self._connection_widget.set_refresh_button_state(False)

    def all_pads_received(self, all_pads: list[str]) -> None:
        pads_available = len(all_pads) > 0
        self._connection_widget.set_dropdown_state(pads_available)
        self._connection_widget.set_connect_button_state(pads_available)
        self._connection_widget.set_refresh_button_state(pads_available)
        self._connection_widget.set_dropdown_items(all_pads)

    def profile_names_received(self, profile_names: list[str]) -> None:
        self._profile_widget.set_dropdown_items(profile_names)

    def pad_connected(self, connected: bool) -> None:
        self._connection_widget.set_dropdown_state(not connected)
        self._connection_widget.set_connect_button_icon(not connected)
        self._connection_widget.set_refresh_button_state(not connected)
