import asyncio
from loguru import logger

from .base_model import BaseSTTModel
from .factory import ModelFactory


class ModelManager:
    def __init__(self):
        self.models: dict[str, "BaseSTTModel"] = {}
        self._lock = asyncio.Lock()
        self.metrics = {
            "total_requests": 0,
            "loaded_models_names": [],
        }

    async def get_model(self, model_name: str) -> "BaseSTTModel":
        """Get model from cache or load it if not present"""
        self.metrics["total_requests"] += 1

        async with self._lock:
            if model_name in self.models:
                logger.debug(f"Model {model_name} found in cache.")
                return self.models[model_name]

        model = ModelFactory.create_model(model_name)
        self.models[model_name] = model
        self.metrics["loaded_models_names"].append(model_name)

        logger.debug(f"Loading model: {model_name}")
        await model.load()
        logger.debug(f"Loaded model: {model_name}")
        return model

    async def cleanup(self):
        """Cleanup all loaded models"""
        async with self._lock:
            for model in self.models.values():
                if hasattr(model, "cleanup"):
                    await model.cleanup()
            self.models.clear()
            self.metrics["loaded_models_names"].clear()

    def get_statistics(self) -> dict:
        """Get current statistics of the ModelManager"""
        return {
            "total_requests": self.metrics["total_requests"],
            "loaded_models_count": len(self.models),
            "loaded_models_names": self.metrics["loaded_models_names"],
        }
