from kokoro import KPipeline
import soundfile as sf
import numpy as np
from text_to_convert import text
import warnings
import time
import io  # Required for in-memory binary handling

warnings.filterwarnings("ignore")

pipeline = KPipeline(
    lang_code="a",
    repo_id='hexgrad/Kokoro-82M' )

# Start timing
start_time = time.time()

# Generate the audio in one pass, without splitting
generator = pipeline(
    text,
    voice="bf_isabella",
    speed=1.2,
    split_pattern=None  # Ensure no splitting
)

# Collect all audio chunks
audio_segments = []

for i, (gs, ps, audio) in enumerate(generator):
    print(f'Processing chunk {i}')
    audio_segments.append(audio)

# Concatenate all audio chunks into one
final_audio = np.concatenate(audio_segments)

# Create an in-memory binary stream
audio_buffer = io.BytesIO()

# Write audio data into the buffer as WAV format
sf.write(audio_buffer, final_audio, 24000, format='WAV')

# Retrieve binary data
audio_binary = audio_buffer.getvalue()

# You can now return, send, or store `audio_binary` directly.
print(f"Generated audio binary of size: {len(audio_binary)} bytes")

# Optionally, reset buffer pointer if needed
audio_buffer.seek(0)

# End timing
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Time taken to generate audio: {elapsed_time:.2f} seconds")
