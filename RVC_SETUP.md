# RVC Voice Cloning Setup Guide

## Overview

RVC (Retrieval-based Voice Conversion) converts speech-to-speech, so we use a two-step pipeline:
1. **Base TTS** generates speech from text (using edge-tts)
2. **RVC** converts that speech to sound like TARS

## Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements-windows.txt
```

This installs:
- `torch` and `torchaudio` - PyTorch for RVC
- `librosa` and `soundfile` - Audio processing
- `faiss-cpu` - Vector search for RVC
- `edge-tts` - Base TTS engine (Microsoft Edge TTS)

### Step 2: Train RVC Model

You need to train an RVC model from your `tars_sample.wav` file. Choose one method:

#### Option A: Google Colab (Recommended - Free GPU)

1. **Open Colab Notebook:**
   - [RVC Training Colab](https://colab.research.google.com/github/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/colab.ipynb)
   - Or search for "RVC training colab" for latest version

2. **Upload TARS Sample:**
   - Upload `voice_samples/tars_sample.wav` to Colab
   - Recommended: 10+ minutes of clean audio

3. **Train Model:**
   - Set epochs: 80 (or more for better quality)
   - Set sample rate: 48000 Hz
   - Click "Run All" and wait ~30 minutes

4. **Download Model:**
   - Download the `.pth` model file
   - Place it at: `models/rvc_models/tars_voice.pth`

#### Option B: Local Training (Requires GPU)

1. **Clone RVC Repository:**
   ```bash
   git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
   cd Retrieval-based-Voice-Conversion-WebUI
   pip install -r requirements.txt
   ```

2. **Prepare Training Data:**
   - Place `tars_sample.wav` in `dataset/tars/raw/`
   - Or use the preprocessing tools in RVC

3. **Train Model:**
   ```bash
   python train.py --dataset tars --epochs 80 --sample_rate 48000
   ```

4. **Copy Model:**
   ```bash
   cp logs/tars/tars_voice.pth ../models/rvc_models/
   ```

#### Option C: Use RVC WebUI

1. **Install RVC WebUI:**
   ```bash
   git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
   cd Retrieval-based-Voice-Conversion-WebUI
   pip install -r requirements.txt
   ```

2. **Launch WebUI:**
   ```bash
   python infer-web.py
   ```

3. **Train via Web Interface:**
   - Go to "Train" tab
   - Upload TARS sample
   - Configure training parameters
   - Start training

### Step 3: Configure App

Add to your `.env` file:

```bash
USE_VOICE_CLONING=true
TARS_VOICE_SAMPLE=voice_samples/tars_sample.wav
RVC_MODEL_PATH=models/rvc_models/tars_voice.pth
BASE_TTS_ENGINE=edge-tts
```

### Step 4: Test

Run the app:

```bash
python main.py
```

You should see:
```
Loading RVC model: models/rvc_models/tars_voice.pth
RVC model loaded successfully on cpu
Initializing base TTS: edge-tts
Base TTS initialized: Microsoft Edge TTS
Voice cloning initialized successfully!
Testing voice generation...
Voice cloning test successful!
TARS voice ready.
```

## Training Requirements

### Audio Sample Requirements

- **Duration:** 10+ minutes recommended (minimum 3 minutes)
- **Quality:** Clear audio, minimal background noise
- **Format:** WAV file, 22050 Hz or 48000 Hz sample rate
- **Content:** TARS dialogue from Interstellar movie

### Training Parameters

- **Epochs:** 80 for basic quality, 200+ for high quality
- **Sample Rate:** 48000 Hz (recommended)
- **Batch Size:** 7 (adjust based on GPU memory)
- **Training Time:** ~30 minutes on GPU, several hours on CPU

## Troubleshooting

### "RVC model not found"

- Ensure model file exists at `models/rvc_models/tars_voice.pth`
- Check file path in `.env` matches actual location
- Verify file permissions

### "Base TTS not available"

- Install edge-tts: `pip install edge-tts`
- Check internet connection (edge-tts requires internet)
- Try alternative: `BASE_TTS_ENGINE=gtts` or `pyttsx3`

### "Failed to load RVC model"

- Verify model file is valid `.pth` file
- Check PyTorch installation: `pip install torch torchaudio`
- Ensure model was trained with compatible RVC version

### Training takes too long

- Use Google Colab (free GPU)
- Reduce epochs (lower quality but faster)
- Use smaller sample rate (22050 Hz instead of 48000 Hz)

### Poor voice quality

- Train with more epochs (200+)
- Use longer/higher quality training sample
- Ensure training sample is clean (no noise/music)
- Try different RVC model versions

## Alternative Base TTS Engines

You can change `BASE_TTS_ENGINE` in `.env`:

- **edge-tts** (default) - Microsoft Edge TTS, good quality, requires internet
- **gtts** - Google TTS, simple, requires internet
- **pyttsx3** - Local, no internet, lower quality

## Model Storage

- Trained model: `models/rvc_models/tars_voice.pth` (~200MB)
- Model can be reused indefinitely
- Backup your model file!

## Performance

- **Generation Time:** ~1-2 seconds per sentence
- **Quality:** Excellent (better than Coqui XTTS)
- **CPU Usage:** Moderate (can run on CPU, GPU faster)
- **Memory:** ~2GB RAM for inference

## Next Steps

After setup:
1. Test with short sentences
2. Test with multi-sentence responses
3. Adjust RVC pitch if needed (in code)
4. Fine-tune training if quality isn't good enough

## Resources

- [RVC Project GitHub](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [RVC Documentation](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki)
- [Training Tutorial](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki/Training)

