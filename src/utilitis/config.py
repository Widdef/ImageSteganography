import tomllib
from pathlib import Path
from typing import Optional

PATH = "config.toml"

class Config:
    def __init__(self, path):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")
        with open(self.path, "rb") as f:
            self._data = tomllib.load(f)

    def get(self, category, key=None, default=None) -> (dict | list | int | str):
        '''
        Returns entire section if key == None
        Returns value for key if key != None
        Returns default value if nothing was found
        '''
        section = self._data.get(category)
        if section is None:
            return default
        if key is None:
            return section
        return section.get(key, default)

_config: Optional[Config] = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config(path=PATH)
    return _config