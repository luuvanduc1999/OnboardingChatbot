from transformers import VitsModel, AutoTokenizer
import torch
from IPython.display import Audio 
import io
model = VitsModel.from_pretrained("facebook/mms-tts-vie") 
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie") 
import soundfile as sf


import torch
import io
import numpy as np

def generate_tts_audio(text):
    """
    Convert text to speech and return a BytesIO WAV buffer.
    """
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs)
        waveform = output.waveform if hasattr(output, "waveform") else output
    audio_np = waveform.squeeze().cpu().numpy()

    # Encode audio to WAV format using soundfile
    buffer = io.BytesIO()
    sf.write(buffer, audio_np, samplerate=16000, format='WAV')
    buffer.seek(0)
    return buffer