import os
import io
import json
import time
import logging
import warnings
import traceback
from typing import List

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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
logger = logging.getLogger("")

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
    traceback.print_exc()
    raise RuntimeError("Failed to load voice choices.")

# =========================
# Pipeline Initialization
# =========================
pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')


# =========================
# Routes
# =========================
@app.get("/voices")
async def get_voices():
    return voice_map

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    voices = list(voice_map.keys())
    return templates.TemplateResponse("index.html", {"request": request, "voices": voices,"api_base_url": API_BASE_URL})

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest):

    try:
        start_time = time.time()

        if request.voice not in voice_map:
            return {"error": "Invalid voice selection."}

        selected_voice = voice_map[request.voice]
        # selected_voice = "bf_alice"
        input_text = request.text
        # speed = request.speed

        processed_text = process_string(input_text)
        generator = pipeline(
            processed_text,
            voice=selected_voice,
            speed=1.0,
            # speed=speed,
            split_pattern=None
        )

        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            logger.info(f"Processing chunk {i}")
            print(f"Processing chunk {i}")
            audio_segments.append(audio)   

        if len(audio_segments) < 1:
            raise HTTPException(detail="need at least one array to concatenate", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        
        final_audio = np.concatenate(audio_segments)

        # Save locally for verification
        sf.write('generated_output.wav', final_audio, 24000)
        logger.info(f"Audio file saved locally as generated_output.wav")



        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, final_audio, 24000, format='WAV')
        audio_buffer.seek(0)

        end_time = time.time()
        logger.info(f"Audio generated in {end_time - start_time:.2f} seconds")

        return StreamingResponse(audio_buffer, media_type="audio/wav", headers={
            "Content-Disposition": "inline; filename=output.wav"
        })
    
    except Exception as e:
        logger.error(f"Error : {e}")
        traceback.print_exc()
        raise HTTPException(detail="Internal server error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR )
