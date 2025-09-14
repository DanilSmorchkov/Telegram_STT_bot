from abc import ABC, abstractmethod
import asyncio
from pathlib import Path


class BaseSTTModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._lifecycle_lock = asyncio.Lock()
        self.is_loaded = False

    @abstractmethod
    async def load(self):
        """Asynchronously load the model"""
        pass

    async def transcribe(self, audio_path: str, language: str) -> str:
        """Safety asynchronously transcribe audio from the given path"""
        async with self._lifecycle_lock:
            if not self.is_loaded:
                await self.load()
            model_ref = self._get_model_ref()

        return await self._transcribe_impl(model_ref, audio_path, language)

    @abstractmethod
    def _get_model_ref(self):
        """Return the model reference after ensuring it's loaded"""
        pass

    @abstractmethod
    async def _transcribe_impl(
        self, model_ref: "BaseSTTModel", audio_path: str, language: str
    ) -> str:
        """Custom implementation of the transcription logic"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Asynchronously cleanup the model resources"""
        pass

    async def ensure_loaded(self):
        """Asynchronously ensure the model is loaded"""
        if not self.is_loaded:
            async with self._lifecycle_lock:
                if not self.is_loaded:
                    await self.load()
                    self.is_loaded = True
