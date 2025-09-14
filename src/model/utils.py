from enum import Enum
import torch


class Language(str, Enum):
    RUSSIAN = "ru"
    ENGLISH = "en"
    FRENCH = "fr"

    @classmethod
    def from_string(cls, value: str) -> "Language":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unsupported language: {value}")


def _get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
