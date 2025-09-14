import aiofiles
import aiofiles.os
from pathlib import Path
import tempfile
import uuid
from loguru import logger


class FileManager:
    """Class to handle asynchronous file operations for audio files"""

    @staticmethod
    async def save_audio_temp(file: bytes, content_type: str) -> str:
        """Asynchronously save the uploaded audio file to a temporary location"""
        file_extension = AudioExtensionMapper.get_extension(content_type)
        filename = f"stt_{uuid.uuid4()}{file_extension}"
        temp_file_path = Path(tempfile.gettempdir()) / filename

        try:
            async with aiofiles.open(temp_file_path, "wb") as out_file:
                await out_file.write(file)
                logger.debug(f"Saved temporary audio file at {temp_file_path}")

            return str(temp_file_path)

        except Exception as e:
            logger.error(f"Failed to save temporary audio file: {e}")
            raise

    @staticmethod
    async def delete_file(file_path: str):
        """Asynchronously delete the specified file"""
        try:
            if await aiofiles.os.path.exists(file_path):
                await aiofiles.os.remove(file_path)
                logger.debug(f"Deleted temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    @staticmethod
    async def cleanup_temp_files():
        """Asynchronously clean up all temporary audio files"""
        try:
            temp_dir = Path(tempfile.gettempdir())
            for temp_file in temp_dir.glob("stt_*"):
                await FileManager.delete_file(str(temp_file))
            logger.info("Cleaned up all temporary audio files.")
        except Exception as e:
            logger.error(f"Failed to clean up temporary files: {e}")



class AudioExtensionMapper:
    """Utility class to map content types to file extensions"""

    CONTENT_TYPE_TO_EXTENSION = {
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/flac": ".flac",
        "audio/ogg": ".ogg",
        "audio/webm": ".webm",
        "audio/aac": ".aac",
        "audio/mp4": ".mp4",
        "audio/x-m4a": ".m4a",
    }

    @classmethod
    def get_extension(cls, content_type: str) -> str:
        """Get the file extension for a given content type"""
        return cls.CONTENT_TYPE_TO_EXTENSION.get(content_type, ".ogg")