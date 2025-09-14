from .whisper import WhisperModel
from .base_model import BaseSTTModel


class ModelFactory:
    @staticmethod
    def create_model(model_name: str, **kwargs) -> BaseSTTModel:
        if model_name.startswith("whisper-"):
            model_size = model_name.split("whisper-")[-1]
            return WhisperModel(model_size=model_size)
        elif model_name == "whisper":
            return WhisperModel(model_size=kwargs.get("size", "small"))
        else:
            raise ValueError(f"Unknown model name: {model_name}")
