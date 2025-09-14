import uuid

from fastapi import FastAPI, File, BackgroundTasks, UploadFile, Query, HTTPException
from fastapi.responses import JSONResponse

from src.model.model_manager import ModelManager
from .file_manager import FileManager
from contextlib import asynccontextmanager

from loguru import logger

VERSION = "0.1.0"

model_manager = ModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown events"""
    logger.info("Starting up the application...")
    logger.info("Preloading default model 'whisper-tiny'...")
    await model_manager.get_model("whisper-tiny")
    logger.info("Default model loaded.")
    yield
    logger.info("Shutting down the application...")
    await model_manager.cleanup()
    await FileManager.cleanup_temp_files()
    logger.info("Cleanup completed.")


app = FastAPI(
    title="Speech-to-Text API",
    description="An API for speech-to-text transcription using various models.",
    version=VERSION,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Speech-to-Text API is running.", "version": VERSION}


@app.get("/health")
async def health_check():
    stats = model_manager.get_statistics()
    return {"status": "healthy", "model_manager_stats": stats}


@app.get("/models")
async def list_models():
    stats = model_manager.get_statistics()
    return {"loaded_models": stats["loaded_models_names"]}


@app.post("/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file to transcribe"),
    model_name: str = Query(
        "whisper-small", description="Model name to use for transcription"
    ),
    language: str = Query("ru", description="Language code of the audio content"),
):
    """Endpoint to transcribe audio files"""
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    request_id = str(uuid.uuid4())
    logger.info(f"Request {request_id}: Received file {file.filename} for model {model_name}")

    try:
        audio_data = await file.read()
        temp_file_path = await FileManager.save_audio_temp(file=audio_data, content_type=file.content_type)
        background_tasks.add_task(FileManager.delete_file, temp_file_path)
        logger.info(f"Request {request_id}: Saved temporary file at {temp_file_path}")

        logger.info(f"Request {request_id}: Getting model {model_name}")
        model = await model_manager.get_model(model_name)
        logger.info(f"Request {request_id}: Model {model_name} loaded, starting transcription")
        text = await model.transcribe(temp_file_path, language=language)
        logger.info(f"Request {request_id}: Success, {len(text)} characters transcribed")

        return JSONResponse({
            "request_id": request_id,
            "model": model_name,
            "language": language,
            "transcription": text,
            "text_length": len(text),
        })

    except Exception as e:
        logger.error(f"Request {request_id}: Failed – {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)