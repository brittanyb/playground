import json
import pathlib
import uuid

import appdirs

from pad_model import PadModel


class ProfileController:
    """Controller for dance pad session data."""

    APP_NAME = "playground"
    APP_AUTHOR = "reflex_creations"
    UNNAMED_PREFIX = "Unnamed Profile"

    def __init__(self, pad_model: PadModel):
        profile_dir = appdirs.user_data_dir(
            self.APP_NAME, self.APP_AUTHOR, roaming=True
        )
        self.profile_path = pathlib.Path(profile_dir)
        if not pathlib.Path.exists(self.profile_path):
            pathlib.Path.mkdir(self.profile_path, parents=True)
        self._saved_data = {}
        self._load_profile_map()
        self._model = pad_model

    def _load_profile_map(self) -> None:
        self._profile_map = {}
        for profile_file in self.profile_path.glob("*.json"):
            with open(profile_file, 'r') as f:
                data = json.load(f)
                self._profile_map[data['name']] = profile_file

    def save_user_profile(self, name: str) -> None:
        if name in self._profile_map:
            profile_path = self._profile_map[name]
        else:
            profile_path = self.profile_path / f"{str(uuid.uuid4())}.json"
        data = {
            "name": name,
            "profile_data": self._model.profile_data
        }
        with open(profile_path, 'w') as f:
            json.dump(data, f, indent=4)
        self._load_profile_map()
        self._saved_data = data['profile_data']

    def load_user_profile(self, name: str) -> None:
        self._load_profile_map()
        profile_path = self._profile_map.get(name)
        if not profile_path:
            raise ValueError(f"No profile found for the name: {name}")
        with open(profile_path, 'r') as f:
            data = json.load(f)
        self._saved_data = data['profile_data']
        self._model.profile_data = self._saved_data

    def create_new_profile(self) -> str:
        index = 1
        profile_name = None
        while profile_name in self.get_profile_names() or profile_name is None:
            profile_name = f"{self.UNNAMED_PREFIX} {index}"
            index += 1
        self.save_user_profile(profile_name)
        return profile_name

    def rename_user_profile(self, old_name: str, new_name: str) -> None:
        if not self._profile_map:
            return
        profile_path = self._profile_map.get(old_name)
        if not profile_path:
            return
        self._profile_map.pop(old_name)
        self._profile_map[new_name] = profile_path
        self.save_user_profile(new_name)

    def remove_user_profile(self, name: str) -> None:
        if not self._profile_map:
            return
        profile_path = self._profile_map.get(name)
        if profile_path and pathlib.Path.exists(profile_path):
            pathlib.Path.unlink(profile_path)
        self._load_profile_map()

    def get_profile_names(self) -> list[str]:
        return sorted(list(self._profile_map.keys()))

    def get_saved_data(self) -> dict:
        return self._saved_data
