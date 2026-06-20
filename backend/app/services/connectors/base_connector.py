from __future__ import annotations

from abc import ABC, abstractmethod

from ..message_normalizer import normalize_message


class BaseConnector(ABC):
    platform: str

    @abstractmethod
    def sync(self, account_id: str) -> list[dict]:
        raise NotImplementedError

    def normalize(self, raw_message: dict) -> dict:
        return normalize_message(raw_message)

