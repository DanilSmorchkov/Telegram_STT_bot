import asyncio
from typing import Optional
from loguru import logger

import whisper
import torch
from .base_model import BaseSTTModel
from .utils import _get_device, Language


class WhisperModel(BaseSTTModel):
    def __init__(self, model_size: str = "small"):
        super().__init__(f"whisper-{model_size}")
        self.model_size = model_size
        self.model: Optional[whisper.Whisper] = None
        self.device = _get_device()

    async def load(self):
        """Asynchronously load the Whisper model"""
        if self.model is not None:
            return

        async with self._lifecycle_lock:
            if self.model is not None:
                return

            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                executor=None,
                func=lambda: whisper.load_model(
                    name=self.model_size, device=self.device
                ),
            )
            self.is_loaded = True

    async def _transcribe_impl(
        self, model_ref: BaseSTTModel, audio_path: str, language: str = "ru"
    ) -> str:
        """Custom implementation of the transcription logic"""
        logger.debug(f"Ensuring model is loaded for transcription")
        await self.ensure_loaded()

        language_enum = Language.from_string(language)
        logger.debug(f"Language is {language_enum.value}")

        logger.debug(f"Transcribing {audio_path}")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor=None,
            func=lambda: whisper.transcribe(
                model=self.model,
                audio=str(audio_path),
                language=language_enum.value,
                fp16=self.device == "cuda",
            ),
        )

        return result["text"]

    def _get_model_ref(self):
        """Return the model reference after ensuring it's loaded"""
        if self.model is None:
            raise RuntimeError("Model is not loaded")
        return self.model

    async def cleanup(self):
        """Asynchronously cleanup the model resources"""
        async with self._lifecycle_lock:
            if self.model is not None:
                del self.model
                self.model = None
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                self.is_loaded = False
