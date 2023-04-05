from typing import Any
from urllib import request

from git import Repo
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        Repo.clone_from("https://github.com/vnegnev/marcos_client.git", "src/sequences/marcos_client")
