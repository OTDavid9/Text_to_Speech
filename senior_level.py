import os
import io
import json
import time
import logging
import warnings
from typing import List

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from dotenv import load_dotenv
import soundfile as sf
import numpy as np

from kokoro import KPipeline
from text_processing import process_string
from models import AudioRequest

# =========================
# App Initialization
# =========================
load_dotenv()
warnings.filterwarnings("ignore")

API_BASE_URL = os.getenv('API_BASE_URL')
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL environment variable not set.")

app = FastAPI(
    root_path="/tts",
    title="Kokoro Text to Speech API",
    description="A Text-to-Speech API powered by Kokoro.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Logging Setup
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kokoro-tts")

# =========================
# Static Files & Templates
# =========================
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# =========================
# Load Voice Map
# =========================
try:
    with open('voice_choices.json', 'r', encoding='utf-8') as f:
        voice_map = json.load(f)
except Exception as e:
    logger.error(f"Error loading voice choices: {e}")
    raise RuntimeError("Failed to load voice choices.")

# =========================
# Pipeline Initialization
# =========================
pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')


# =========================
# Routes
# =========================
@app.get("/voices", response_model=List[str])
async def get_voices():
    return list(voice_map.keys())


@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    voices = list(voice_map.keys())
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "voices": voices, "api_base_url": API_BASE_URL}
    )


@app.post("/generate-audio")
async def generate_audio(request: AudioRequest, background_tasks: BackgroundTasks):
    start_time = time.time()

    # Input Validation
    if request.voice not in voice_map:
        logger.warning(f"Invalid voice selection: {request.voice}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid voice selection."
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text cannot be empty."
        )

    if len(request.text) > 100000000:  # Arbitrary limit, can adjust
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Input text is too long. Please limit to 1000 characters."
        )

    selected_voice = voice_map[request.voice]
    logger.info(f"Generating audio for voice: {selected_voice}")

    try:
        processed_text = process_string(request.text)

        generator = pipeline(
            processed_text,
            voice=selected_voice,
            speed=1.3,
            split_pattern=None
        )

        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            logger.info(f"Processing chunk {i + 1}")
            audio_segments.append(audio)

        # Concatenate audio segments using a threadpool to avoid blocking
        final_audio = await run_in_threadpool(np.concatenate, audio_segments)

        # Save locally for verification in background
        background_tasks.add_task(save_audio_locally, final_audio)

        # Stream the audio
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, final_audio, 24000, format='WAV')
        audio_buffer.seek(0)

        duration = time.time() - start_time
        logger.info(f"Audio generated successfully in {duration:.2f} seconds")

        return StreamingResponse(
            audio_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=output.wav"}
        )

    except Exception as e:
        logger.error(f"Error during audio generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating audio."
        )


# =========================
# Background Task
# =========================
def save_audio_locally(audio_data: np.ndarray):
    try:
        sf.write('generated_output.wav', audio_data, 24000)
        logger.info("Audio file saved locally as 'generated_output.wav'")
    except Exception as e:
        logger.error(f"Failed to save audio locally: {e}")


# =========================
# Global Exception Handler
# =========================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "senior_level:app",  # Replace with your actual filename without .py
        host="localhost",          # Accept connections from any IP
        port=7000,               # Or any port you want
        reload=True              # Auto-reload on code changes (development only)
    )