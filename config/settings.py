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

# RVC settings
RVC_MODELS_DIR = MODELS_DIR / 'rvc_models'
RVC_MODELS_DIR.mkdir(exist_ok=True)
RVC_MODEL_PATH = os.getenv('RVC_MODEL_PATH', str(RVC_MODELS_DIR / 'tars_voice.pth'))
BASE_TTS_ENGINE = os.getenv('BASE_TTS_ENGINE', 'edge-tts')  # edge-tts, gtts, or pyttsx3

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

# Validate RVC model exists (will be checked in voice_cloning.py, but warn here)
if not os.path.exists(RVC_MODEL_PATH):
    print(f"WARNING: RVC model not found: {RVC_MODEL_PATH}")
    print("The app will exit on startup if model is not found.")
    print("See RVC_SETUP.md for training instructions.")

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

