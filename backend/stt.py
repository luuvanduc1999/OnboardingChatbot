import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf
import subprocess
import os
import tempfile
from scipy.signal import resample_poly

MODEL_NAME = "nguyenvulebinh/wav2vec2-base-vietnamese-250h"

try:
    print("Loading Wav2Vec2 model for Vietnamese...")
    processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
    STT_AVAILABLE = True
    print("STT model loaded successfully.")
except Exception as e:
    print(f"Error loading STT model: {e}")
    STT_AVAILABLE = False


def convert_to_wav16k(input_path):
    """
    Dùng ffmpeg để convert mọi định dạng audio sang wav 16kHz mono
    """
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",          # mono
        "-ar", "16000",      # 16kHz
        tmp_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tmp_wav


def transcribe(audio_path: str) -> str:
    if not STT_AVAILABLE:
        return "[STT model not available]"

    # Chuyển audio sang WAV 16kHz mono
    wav_path = convert_to_wav16k(audio_path)

    # Đọc file wav
    speech, sample_rate = sf.read(wav_path)

    # Nếu không phải 16kHz (trường hợp ffmpeg lỗi), resample lại
    if sample_rate != 16000:
        speech = resample_poly(speech, 16000, sample_rate)
        sample_rate = 16000

    # Xử lý audio
    input_values = processor(speech, sampling_rate=sample_rate, return_tensors="pt", padding=True).input_values

    # Suy luận
    with torch.no_grad():
        logits = model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]

    # Xóa file tạm
    os.remove(wav_path)

    return transcription.lower()
