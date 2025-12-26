"""Configuration and settings management."""

import os
from pathlib import Path
from dotenv import load_dotenv
from utils.platform_detector import get_platform, get_whisper_model, get_tts_config

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Platform detection
PLATFORM = get_platform()
IS_WINDOWS = PLATFORM == 'windows'
IS_RASPBERRY_PI = PLATFORM == 'raspberry_pi'

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file")

# Personality defaults
DEFAULT_HUMOR = int(os.getenv('DEFAULT_HUMOR', '75'))
DEFAULT_HONESTY = int(os.getenv('DEFAULT_HONESTY', '90'))
SAVE_HISTORY_DEFAULT = os.getenv('SAVE_HISTORY_DEFAULT', 'false').lower() == 'true'

# Model configuration
WHISPER_MODEL = os.getenv('WHISPER_MODEL') or get_whisper_model()
TTS_CONFIG = get_tts_config()

# Paths
MODELS_DIR = BASE_DIR / 'models'
CACHE_DIR = BASE_DIR / 'cache'
DATABASE_PATH = BASE_DIR / 'conversations.db'
AUDIO_CACHE_DIR = BASE_DIR / 'audio_cache'
VOICE_SAMPLES_DIR = BASE_DIR / 'voice_samples'

# Voice cloning settings - MANDATORY (no fallback)
USE_VOICE_CLONING = os.getenv('USE_VOICE_CLONING', 'true').lower() == 'true'
TARS_VOICE_SAMPLE = os.getenv('TARS_VOICE_SAMPLE', str(VOICE_SAMPLES_DIR / 'tars_sample.wav'))

# GPT-SoVITS settings
GPTSOVITS_MODELS_DIR = MODELS_DIR / 'gptsovits_models'
GPTSOVITS_MODELS_DIR.mkdir(exist_ok=True)
GPTSOVITS_MODEL_DIR = os.getenv('GPTSOVITS_MODEL_DIR', str(GPTSOVITS_MODELS_DIR / 'tars_voice'))
GPTSOVITS_USE_ONNX = os.getenv('GPTSOVITS_USE_ONNX', 'true').lower() == 'true'
GPTSOVITS_QUANTIZED = os.getenv('GPTSOVITS_QUANTIZED', 'false').lower() == 'true'

# Validate voice cloning requirements on import
if not USE_VOICE_CLONING:
    import sys
    print("ERROR: Voice cloning is required. Set USE_VOICE_CLONING=true in .env")
    sys.exit(1)

if not os.path.exists(TARS_VOICE_SAMPLE):
    import sys
    print(f"ERROR: TARS voice sample not found: {TARS_VOICE_SAMPLE}")
    print("Please place a TARS voice sample WAV file at this location")
    sys.exit(1)

# Validate GPT-SoVITS model exists (will be checked in voice_cloning.py, but warn here)
model_dir = Path(GPTSOVITS_MODEL_DIR)
onnx_dir = model_dir / 'onnx'
if GPTSOVITS_USE_ONNX:
    if not onnx_dir.exists():
        print(f"WARNING: GPT-SoVITS ONNX models not found: {onnx_dir}")
        print("The app will exit on startup if models are not found.")
        print("See GPTSOVITS_SETUP.md for training and export instructions.")
    else:
        gpt_model = onnx_dir / ('tars_gpt_int8.onnx' if GPTSOVITS_QUANTIZED else 'tars_gpt_fp32.onnx')
        vits_model = onnx_dir / ('tars_vits_int8.onnx' if GPTSOVITS_QUANTIZED else 'tars_vits_fp32.onnx')
        if not gpt_model.exists() or not vits_model.exists():
            print(f"WARNING: GPT-SoVITS ONNX model files not found")
            print(f"Expected: {gpt_model} and {vits_model}")
            print("Run: python scripts/export_onnx.py --model-dir", model_dir)
else:
    # Check for PyTorch models
    s1_models = list(model_dir.glob('**/*s1*.pth')) + list(model_dir.glob('**/*gpt*.pth'))
    s2_models = list(model_dir.glob('**/*s2*.pth')) + list(model_dir.glob('**/*vits*.pth'))
    if not s1_models or not s2_models:
        print(f"WARNING: GPT-SoVITS PyTorch models not found: {model_dir}")
        print("The app will exit on startup if models are not found.")
        print("See GPTSOVITS_SETUP.md for training instructions.")

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
AUDIO_CACHE_DIR.mkdir(exist_ok=True)
VOICE_SAMPLES_DIR.mkdir(exist_ok=True)

# Gemini API settings
GEMINI_MODEL = 'gemini-2.0-flash-exp'  # Latest Flash model for low latency

# Performance settings
STREAMING_ENABLED = True
CACHE_ENABLED = True
MAX_CACHE_SIZE = 100  # Number of cached responses

