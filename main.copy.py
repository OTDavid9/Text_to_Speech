from kokoro import KPipeline
import soundfile as sf
import numpy as np
from text_to_convert import text
import warnings
import time

warnings.filterwarnings("ignore")

pipeline = KPipeline(lang_code="a")

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

# Save as a single audio file
sf.write('final_output.wav', final_audio, 24000)

# End timing
end_time = time.time()
elapsed_time = end_time - start_time

print("Audio file 'final_output.wav' generated successfully.")
print(f"Time taken to generate audio: {elapsed_time:.2f} seconds")
