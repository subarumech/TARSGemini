# TARS AI Assistant

A cross-platform AI assistant inspired by TARS from Interstellar, featuring speech recognition, Gemini API integration, and geometric block animations.

## Features

- **Speech Recognition**: faster-whisper for accurate, offline speech-to-text
- **AI Responses**: Google Gemini API integration with streaming
- **Text-to-Speech**: GPT-SoVITS for high-quality custom voice cloning
- **Personality System**: Adjustable humor (0-100%) and honesty (0-100%) settings
- **Conversation History**: Optional persistent storage with toggle control
- **Geometric Animations**: 3D block animations synchronized with speech
- **Cross-Platform**: Optimized for both Windows PC and Raspberry Pi

## Architecture

The assistant uses a streaming pipeline architecture for minimal latency:
- Parallel processing of STT, LLM, and TTS
- Sentence-level streaming for immediate response
- Response caching for common queries (93% latency reduction)

## Installation

### Windows

```bash
pip install -r requirements-windows.txt
```

### Raspberry Pi

```bash
pip install -r requirements-pi.txt
# Run setup script for model downloads
python scripts/setup_pi.py
```

## Configuration

1. Create a `.env` file in the project root
2. Add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_HUMOR=75
DEFAULT_HONESTY=90
SAVE_HISTORY_DEFAULT=false
```

See `SETUP.md` for detailed setup instructions.

## Voice Cloning Setup

To use custom TARS voice:

1. **Prepare training data**: Place `tars_sample.wav` in `voice_samples/`
2. **Setup GPT-SoVITS**: `python scripts/setup_gptsovits.py`
3. **Train model**: `python scripts/train_gptsovits.py --audio voice_samples/tars_sample.wav`
4. **Export ONNX**: `python scripts/export_onnx.py --model-dir models/gptsovits_models/tars_voice`

See `GPTSOVITS_SETUP.md` for detailed training instructions.

## Usage

```bash
python main.py
```

## Performance

- **Windows PC**: 200-350ms perceived latency
- **Raspberry Pi 5**: 250-450ms perceived latency
- **Raspberry Pi 4**: 400-700ms perceived latency

## Project Structure

```
FromScratchTARS/
├── config/          # Configuration and settings
├── core/            # Core functionality (STT, TTS, Gemini, pipeline)
├── personality/     # TARS personality engine
├── gui/             # PyQt5 interface and animations
├── utils/           # Utility functions
└── main.py          # Entry point
```

## License

MIT

