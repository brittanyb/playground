import json
import pathlib
import uuid

import appdirs

from pad_model import PadModel


class ProfileController:
    """Controller for a single user profile of pad session data."""

    APP_NAME = "playground"
    APP_AUTHOR = "reflex_creations"

    def __init__(self):
        profile_dir = appdirs.user_data_dir(
            self.APP_NAME, self.APP_AUTHOR, roaming=True
        )
        self.profile_path = pathlib.Path(profile_dir)
        if not pathlib.Path.exists(self.profile_path):
            pathlib.Path.mkdir(self.profile_path, parents=True)
        self.profile_map = self._load_profile_map()

    def _load_profile_map(self) -> dict:
        profile_map = {}
        for profile_file in self.profile_path.glob("*.json"):
            with open(profile_file, 'r') as f:
                data = json.load(f)
                profile_map[data['name']] = profile_file
        return profile_map

    def save_user_profile(self, pad_model: PadModel, name: str) -> None:
        if name in self.profile_map:
            profile_path = self.profile_map[name]
        else:
            profile_path = self.profile_path / f"{str(uuid.uuid4())}.json"
        data = {
            "name": name,
            "profile_data": pad_model.profile_data
        }
        with open(profile_path, 'w') as f:
            json.dump(data, f, indent=4)
        self.profile_map = self._load_profile_map()

    def load_user_profile(self, name: str) -> PadModel:
        profile_path = self.profile_map.get(name)
        if not profile_path:
            raise ValueError(f"No profile found for the name: {name}")
        with open(profile_path, 'r') as f:
            data = json.load(f)
        pad_model = PadModel()
        pad_model.profile_data = data['profile_data']
        return pad_model

    @property
    def profiles(self) -> list[pathlib.Path]:
        return list(self.profile_map.keys())
