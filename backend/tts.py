import io
import numpy as np

try:
    from transformers import VitsModel, AutoTokenizer
    import torch
    import soundfile as sf
    
    model = VitsModel.from_pretrained("facebook/mms-tts-vie") 
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie") 
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: TTS libraries not available. TTS functionality will be disabled.")

def generate_tts_audio(text):
    """
    Convert text to speech and return a BytesIO WAV buffer.
    """
    if not TTS_AVAILABLE:
        # Return empty audio buffer as fallback
        buffer = io.BytesIO()
        # Create a simple silence audio
        silence = np.zeros(16000, dtype=np.float32)  # 1 second of silence
        try:
            import wave
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes((silence * 32767).astype(np.int16).tobytes())
        except:
            pass
        buffer.seek(0)
        return buffer
    
    try:
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
    except Exception as e:
        print(f"TTS Error: {e}")
        # Return empty buffer on error
        buffer = io.BytesIO()
        buffer.seek(0)
        return buffer