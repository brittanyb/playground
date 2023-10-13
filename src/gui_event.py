class GUIEvent:
    """Data class describing GUI events triggered by widgets."""

    REFRESH = "GUI_refresh_pads"
    CONNECT = "GUI_connect_pad"
    NEW = "GUI_new_profile"
    REMOVE = "GUI_remove_profile"
    RENAME = "GUI_rename_profile"
    SAVE = "GUI_save_profile"
    SELECT = "GUI_select_profile"
    INIT = "GUI_init_window"
