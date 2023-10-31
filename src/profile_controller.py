import pathlib
import pickle
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
        self._model = pad_model

    def _load_profile_map(self) -> None:
        self._profile_map = {}
        for profile_file in self.profile_path.glob("*.pkl"):
            with open(profile_file, 'rb') as f:
                data = pickle.load(f)
                self._profile_map[data[0]] = profile_file

    def initialise_profile(self) -> list[str]:
        self._load_profile_map()
        if names := self.get_profile_names():
            self.load_user_profile(names[0])
        else:
            name = self.create_new_profile()
            names = [name]
            self.load_user_profile(name)
        return names

    def save_user_profile(self, name: str) -> bool:
        if name in self._profile_map:
            profile_path = self._profile_map[name]
        else:
            profile_path = self.profile_path / f"{str(uuid.uuid4())}.pkl"
        data = (name, self._model.profile_data)
        with open(profile_path, 'wb') as f:
            pickle.dump(data, f)
        self._load_profile_map()
        self._saved_data = data[1]
        self._model.set_saved()
        return True

    def load_user_profile(self, name: str) -> str:
        self._load_profile_map()
        profile_path = self._profile_map.get(name)
        if not profile_path:
            raise ValueError(f"No profile found for {name}.")
        with open(profile_path, 'rb') as f:
            data = pickle.load(f)
        self._saved_data = data[1]
        self._model.profile_data = self._saved_data
        return name

    def create_new_profile(self) -> str:
        index = 1
        profile_name = None
        while profile_name in self.get_profile_names() or profile_name is None:
            profile_name = f"{self.UNNAMED_PREFIX} {index}"
            index += 1
        self.save_user_profile(profile_name)
        return profile_name

    def rename_user_profile(
        self, old: str, new_name: tuple[bool, str]
    ) -> tuple[str, str]:
        if not new_name[0]:
            return (old, old)
        new = new_name[1]
        if new.isspace() or new == "" or new in self.get_profile_names():
            return (old, old)
        if not self._profile_map:
            raise RuntimeError("Profile map not available.")
        profile_path = self._profile_map.get(old)
        if not profile_path:
            raise ValueError(f"{profile_path} not found.")
        self._profile_map.pop(old)
        self._profile_map[new] = profile_path
        self.save_user_profile(new)
        return (old, new)

    def remove_user_profile(self, name: str) -> bool:
        if not self._profile_map:
            return False
        profile_path = self._profile_map.get(name, None)
        if not (profile_path and pathlib.Path.exists(profile_path)):
            return False
        pathlib.Path.unlink(profile_path)
        self._load_profile_map()
        self.load_user_profile(self.get_profile_names()[0])
        return True

    def get_profile_names(self) -> list[str]:
        return sorted(list(self._profile_map.keys()))

    def get_saved_data(self) -> dict:
        return self._saved_data
