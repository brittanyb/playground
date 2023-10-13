from connection_widget import ConnectionWidget
from pad_widget import PadWidget
from profile_widget import ProfileWidget


class GUIEventHandler:
    """Methods to run on widgets when data is received from interface."""

    def __init__(
        self, connection_widget: ConnectionWidget, pad_widget: PadWidget,
        profile_widget: ProfileWidget
    ):
        self._connection_widget = connection_widget
        self._pad_widget = pad_widget
        self._profile_widget = profile_widget

    def initialise_widgets(self, data: list) -> None:
        pad_list = data[0]
        profile_list = data[1]
        active = False
        if len(pad_list) > 0:
            active = True
        self._connection_widget.set_dropdown(active, pad_list)
        self._profile_widget.set_dropdown_items(profile_list)
