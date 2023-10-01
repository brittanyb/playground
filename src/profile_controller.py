import json
import pathlib
import uuid

import appdirs

from pad_model import PadModel


class ProfileController:
    """"""

    APP_NAME = "playground"
    APP_AUTHOR = "reflex_creations"

    def __init__(self):
        profile_dir = appdirs.user_data_dir(
            self.APP_NAME, self.APP_AUTHOR, roaming=True
        )
        profile_path = pathlib.Path(profile_dir)
        if not pathlib.Path.exists(profile_path):
            pathlib.Path.mkdir(profile_path, parents=True)

    def save_user_profile(self):
        pass

    def load_user_profile(self):
        pass

    @property
    def profiles(self) -> list[pathlib.Path]:
        return list()
