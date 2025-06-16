from fastapi import FastAPI, Request, Form
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

warnings.filterwarnings("ignore")

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse)
def serve_homepage(request: Request):
    voices = list(voice_map.keys())
    return templates.TemplateResponse("index.html", {"request": request, "voices": voices})

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

# @app.post("/generate-audio")
# async def generate_audio(request: Request, text: str = Form(...), voice: str = Form(...)):
#     start_time = time.time()

#     if voice not in voice_map:
#         return {"error": "Invalid voice selection."}

#     selected_voice = voice_map[voice]

#     generator = pipeline(
#         text,
#         voice=selected_voice,
#         speed=1.2,
#         split_pattern=None
#     )

#     audio_segments = []

#     for i, (gs, ps, audio) in enumerate(generator):
#         print(f'Processing chunk {i}')
#         audio_segments.append(audio)

#     final_audio = np.concatenate(audio_segments)

#     # Save locally for verification
#     sf.write('generated_output.wav', final_audio, 24000)
#     print(f"Audio file saved locally as generated_output.wav")

#     audio_buffer = io.BytesIO()
#     sf.write(audio_buffer, final_audio, 24000, format='WAV')
#     audio_buffer.seek(0)

#     end_time = time.time()
#     print(f"Audio generated in {end_time - start_time:.2f} seconds")

#     return StreamingResponse(audio_buffer, media_type="audio/wav", headers={
#         "Content-Disposition": "inline; filename=output.wav"
#     })

# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.responses import StreamingResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from kokoro import KPipeline
# import soundfile as sf
# import numpy as np
# import io
# import warnings
# import time
# from pydantic import BaseModel
# import json


# warnings.filterwarnings("ignore")

# app = FastAPI()

# # Prepare the pipeline globally to save load time
# pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')

# # Serve static files (CSS, JS, images) if needed
# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")


# class TextToConvert(BaseModel):
#     text: str
#     voice: str

# with open('voice_choices.json', 'r', encoding='utf-8') as f:
#     voice_map = json.load(f)

# @app.get("/", response_class=HTMLResponse)
# def serve_homepage(request: Request):
#     voices = list(voice_map.keys())
#     return templates.TemplateResponse("index.html", {"request": request, "voices": voices})


# @app.get("/generate-audio")
# def audio_get_not_allowed():
#     return {"message": "Please use POST method to generate audio."}

# @app.post("/generate-audio")
# def generate_audio(request: TextToConvert):
#     start_time = time.time()

#     input_text = request.text
#     voice_key = request.voice

#     if voice_key not in voice_map:
#         return {"error": "Invalid voice selection."}

#     selected_voice = voice_map[voice_key] 
#     # Generate audio
#     generator = pipeline(
#         input_text,
#         voice= selected_voice,
#         speed=1.2,
#         split_pattern=None
#     )

#     audio_segments = []

#     for i, (gs, ps, audio) in enumerate(generator):
#         print(f'Processing chunk {i}')
#         audio_segments.append(audio)

#     # Merge audio parts
#     final_audio = np.concatenate(audio_segments)

#     # Save locally for verification
#     local_filename = 'generated_output.wav'
#     sf.write(local_filename, final_audio, 24000)
#     print(f"Audio file saved locally as {local_filename}")

#     # Prepare in-memory buffer for streaming
#     audio_buffer = io.BytesIO()
#     sf.write(audio_buffer, final_audio, 24000, format='WAV')
#     audio_buffer.seek(0)

#     end_time = time.time()
#     print(f"Audio generated and ready in {end_time - start_time:.2f} seconds")

#     # Stream the audio response
#     return StreamingResponse(audio_buffer, media_type="audio/wav", headers={
#         "Content-Disposition": "inline; filename=output.wav"
#     })
