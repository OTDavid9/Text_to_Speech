from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import io
import json
import warnings
import time
import os 
from dotenv import load_dotenv

load_dotenv()


warnings.filterwarnings("ignore")

API_BASE_URL = os.getenv('API_BASE_URL')
app = FastAPI(root_path="/tts")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains later
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load voices
with open('voice_choices.json', 'r', encoding='utf-8') as f:
    voice_map = json.load(f)

pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')

@app.get("/voices")
def get_voices():
    return voice_map

@app.get("/", response_class=HTMLResponse)
def serve_homepage(request: Request):
    voices = list(voice_map.keys())
    return templates.TemplateResponse("index.html", {"request": request, "voices": voices,  "api_base_url": API_BASE_URL})

class AudioRequest(BaseModel):
    text: str
    voice: str

@app.post("/generate-audio")
async def generate_audio(request: AudioRequest):
    start_time = time.time()

    if request.voice not in voice_map:
        return {"error": "Invalid voice selection."}

    selected_voice = voice_map[request.voice]

    generator = pipeline(
        request.text,
        voice=selected_voice,
        speed=1.2,
        split_pattern=None
    )

    audio_segments = []

    for i, (gs, ps, audio) in enumerate(generator):
        print(f'Processing chunk {i}')
        audio_segments.append(audio)

    

    final_audio = np.concatenate(audio_segments)

    # Save locally for verification
    sf.write('generated_output.wav', final_audio, 24000)
    print(f"Audio file saved locally as generated_output.wav")

    audio_buffer = io.BytesIO()
    sf.write(audio_buffer, final_audio, 24000, format='WAV')
    audio_buffer.seek(0)

    end_time = time.time()
    print(f"Audio generated in {end_time - start_time:.2f} seconds")

    return StreamingResponse(audio_buffer, media_type="audio/wav", headers={
        "Content-Disposition": "inline; filename=output.wav"
    })
