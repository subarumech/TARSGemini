# TTS Learnings: GPT-SoVITS Training Guide

## Overview

GPT-SoVITS is a high-quality text-to-speech system that uses a two-stage architecture:
1. **GPT Model (Stage 1)**: Generates prosody and rhythm from text
2. **VITS Model (Stage 2)**: Synthesizes high-quality waveform audio

This guide covers everything learned about setting up, training, and troubleshooting GPT-SoVITS for TARS voice cloning on Windows.

---

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.10.11 (from python.org, NOT Microsoft Store)
- **GPU**: NVIDIA GPU with CUDA support (RTX 2060 SUPER or better recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 20GB+ free space for models and training data
- **Dependencies**: FFmpeg, NLTK data, PyTorch 2.6+

---

## Critical Setup Requirements

### 1. Python Version

**Issue**: Python 3.13 is incompatible with GPT-SoVITS dependencies
- `numpy<2.0` requires compilation which fails on Python 3.13
- Windows Store Python has restricted permissions and can't compile packages

**Solution**: 
- Use Python 3.10.11 from python.org (NOT Windows Store version)
- Create a virtual environment: `python -m venv venv310`
- Always activate the venv before running any GPT-SoVITS commands

### 2. PyTorch Version Security Issue

**Issue**: `torch 2.5.x` has a security vulnerability (CVE-2025-32434) that prevents loading pretrained models

**Error Message**:
```
ValueError: Due to a serious vulnerability issue in `torch.load`, even with `weights_only=True`, 
we now require users to upgrade torch to at least v2.6
```

**Solution**:
```bash
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### 3. Port Conflicts

**Issue**: Port 9874 already in use from previous WebUI sessions

**Error Message**:
```
OSError: Cannot find empty port in range: 9874-9874
```

**Solution**:
```bash
# Windows PowerShell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Or find specific process
netstat -ano | findstr :9874
taskkill /PID <PID> /F
```

### 4. FFmpeg Missing

**Issue**: Audio slicing and processing requires FFmpeg

**Error Message**:
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solution**:
```bash
winget install Gyan.FFmpeg
# Or download from https://ffmpeg.org/
```

---

## Initial Setup

### Quick Setup Commands

```bash
# Install Python 3.10.11 from python.org
# Create venv
cd "path\to\FromScratchTARS"
python -m venv venv310

# Activate venv
.\venv310\Scripts\activate

# Install dependencies
cd models\GPT-SoVITS
pip install -r requirements.txt

# Upgrade PyTorch
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Download NLTK data
python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng'); nltk.download('cmudict'); nltk.download('punkt')"

# Install FFmpeg
winget install Gyan.FFmpeg
```

### Manual Setup (Alternative)

If automated setup fails:

1. **Clone Repository**:
   ```bash
   cd models
   git clone https://github.com/RVC-Boss/GPT-SoVITS.git
   cd GPT-SoVITS
   ```

2. **Install PyTorch** (Windows CUDA):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install librosa soundfile audioread cn2an jieba onnx onnxruntime ffmpeg-python
   ```

---

## Audio Preparation

### Requirements

- **Minimum recommended**: 1-2 minutes of clean audio
- **Better results**: 5-10 minutes of varied dialogue
- **Best results**: 10+ minutes with diverse speech patterns
- **Format**: WAV, MP3, or other common formats
- **Quality**: Clear speech, minimal background noise

### Audio Processing

Audio files should be:
- Converted from MP3 to WAV format
- Normalized for consistent volume
- Set to 22050Hz sample rate (mono)
- Saved to: `models\GPT-SoVITS\dataset\tars\raw\`

### Extracting TARS Audio

**Option A: Using FFmpeg**
```bash
# Extract 30 seconds starting at specific time
ffmpeg -i interstellar.mp4 -ss 01:23:45 -t 00:00:30 -vn -acodec pcm_s16le -ar 22050 -ac 1 tars_clip.wav
```

**Option B: Using Audacity (Manual)**
1. Open movie file in Audacity
2. Find TARS dialogue scenes
3. Select and copy TARS-only audio
4. Remove background noise (Effect > Noise Reduction)
5. Export as WAV (File > Export > Export as WAV)

**Audio Cleaning Tips**:
1. Remove background noise: Use Audacity's noise reduction
2. Normalize volume: Ensure consistent levels
3. Remove music: Isolate voice-only segments
4. Split long clips: Break into 10-30 second segments if needed

---

## Training Process

### Step-by-Step Training Workflow

#### Step 1: Start GPT-SoVITS WebUI

```powershell
cd models\GPT-SoVITS
..\..\venv310\Scripts\python.exe webui.py
```

The WebUI will open at: **http://127.0.0.1:9874**

#### Step 2: Speech Slicing (Tab: 1A-Speech Slicing Tool)

This splits your audio files into smaller segments suitable for training.

**Settings:**
- **Input audio folder**: `dataset\tars\raw`
- **Output folder**: `dataset\tars\sliced`
- **Minimum audio duration**: `2` seconds
- **Maximum audio duration**: `12` seconds
- **Language**: Leave as default (auto-detect)

**Action:** Click **"Slice Audio"**

**Expected result:** Audio files split into segments in `dataset\tars\sliced\`

#### Step 3: Speech Recognition (Tab: 1A-Speech Recognition Tool)

This generates text transcriptions of your audio using ASR (Automatic Speech Recognition).

**Settings:**
- **Input folder**: `dataset\tars\sliced`
- **Output folder**: `dataset\tars\asr_output`
- **Language**: `EN` (English)
- **ASR Model**: Use default (FasterWhisper or FunASR)

**Action:** Click **"Run ASR"**

**Expected result:** Creates `dataset\tars\asr_output\sliced.list` with transcriptions

**Format of sliced.list:**
```
audio_path|speaker_name|language|transcription_text
```

#### Step 4: Proofread Transcriptions (Tab: 1A-Speech-to-Text Proofreading Tool)

**CRITICAL STEP** - Don't skip this!

ASR makes mistakes, especially with:
- Character names (TARS, Cooper, Brand, etc.)
- Technical terms
- Movie-specific dialogue

**Settings:**
- **Load file**: `dataset\tars\asr_output\sliced.list`

**Action:**
1. Review each transcription
2. Correct any errors
3. Ensure proper capitalization and punctuation
4. Click **"Save"** when done

**Why this matters:** Poor transcriptions = poor voice quality

#### Step 5: Dataset Formatting (Tab: 1A-Dataset Formatting Tool)

This extracts features from your audio needed for training.

**Settings:**
- **Text labelling file**: `dataset\tars\asr_output\sliced.list`
- **Audio dataset folder**: `dataset\tars\sliced`

**Run these steps IN ORDER:**

##### 5a. Tokenization & BERT Feature Extraction (Button: 1Aa)
- Converts text to phonemes
- Extracts BERT language features
- **If you get NLTK errors**, run:
  ```powershell
  .\venv310\Scripts\python.exe -c "import nltk; nltk.download('averaged_perceptron_tagger_eng'); nltk.download('cmudict'); nltk.download('punkt')"
  ```

##### 5b. Speech SSL Feature Extraction (Button: 1Ab)
- Extracts HuBERT features from audio
- Takes the longest time

##### 5c. Semantics Token Extraction (Button: 1Ac)
- Extracts semantic tokens

##### 5d. One-Click Formatting (Button: 1Aabc)
- Combines all features
- Prepares final training dataset

**Expected result:** All features extracted and saved to `logs\tars\`

#### Step 6: Fine-Tuning (Tab: 1B-Fine-Tuning)

Train the models in this order:

##### 6a. Train SoVITS Model (Voice Characteristics)

**Settings:**
- **Experiment name**: `tars` (or `tars2` if continuing)
- **Model version**: `v2Pro` or `v2ProPlus`
- **Batch size**: Start with `4` (adjust based on GPU memory)
- **Epochs**: `8-12` for initial training
- **Save frequency**: Every `4` epochs

**Action:** Click **"Start SoVITS Training"**

**Monitor:** Watch the loss values decrease in the training log

##### 6b. Train GPT Model (Prosody/Speaking Patterns)

**Settings:**
- **Use the SoVITS model** you just trained
- **Batch size**: `4-8`
- **Epochs**: `10-15`
- **Save frequency**: Every `5` epochs

**Action:** Click **"Start GPT Training"**

**Expected result:** Trained models saved to:
- `SoVITS_weights_v2Pro\` or `SoVITS_weights_v2ProPlus\`
- `GPT_weights_v2Pro\` or `GPT_weights_v2ProPlus\`

---

## Training Tips

1. **Start small**: Train for fewer epochs first, test the output, then continue training if needed
2. **Monitor loss**: Training loss should steadily decrease. If it plateaus or increases, you may be overfitting
3. **Save checkpoints**: Keep multiple checkpoints so you can compare quality
4. **Test frequently**: Generate samples during training to check progress
5. **Add more data**: If quality isn't good enough, extract more TARS dialogue and retrain

### Training Parameters

**Key Parameters:**
- `batch-size`: Larger = faster training but more VRAM (default: auto-detected)
- `epochs`: More epochs = better quality but longer training (default: auto-detected)
- `dataset`: Path to prepared dataset directory

**Training Time Estimates:**
- Windows (RTX 3080): ~30 minutes for 30 epochs
- Mac M1: ~1-2 hours for 20 epochs
- CPU Only: ~4-6 hours for 10 epochs (not recommended)

---

## Troubleshooting

### NLTK Data Requirements

**Issue**: Missing English Language Processing Data

**Error Message**:
```
LookupError: Resource averaged_perceptron_tagger_eng not found
```

**When it occurs**: During "Tokenization & BERT Feature Extraction" step when processing English text

**Solution**:
```python
python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng'); nltk.download('averaged_perceptron_tagger'); nltk.download('cmudict'); nltk.download('punkt')"
```

**Why**: GPT-SoVITS needs NLTK's part-of-speech tagger and pronunciation dictionary to convert English text to phonemes for training.

### Unicode/Encoding Issues

**Issue**: Windows console (cp1252) can't display Chinese characters or special Unicode

**Error Message**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\uffe5'
```

**Solution**: Modified `tools/slice_audio.py` to use UTF-8 binary output:
```python
import sys
message = f"成功{len(todo)}个".encode('utf-8')
sys.stdout.buffer.write(message)
sys.stdout.buffer.write(b'\n')
```

**Files affected**:
- `models/GPT-SoVITS/tools/slice_audio.py`

### Gradio/Pydantic Compatibility Issues

**Issue**: Proofreading Tool "No API Found" Error

**Error Message**:
```
TypeError: argument of type 'bool' is not iterable
```

**Root Cause**: Incompatibility between Gradio 4.44.1, Pydantic 2.12.5, and gradio_client schema processing

**Solution**:
1. Downgrade Gradio and Pydantic:
```bash
pip install gradio==4.36.1 pydantic==2.10.6
```

2. Patch `venv310\lib\site-packages\gradio_client\utils.py` line ~1092:
```python
# Original (causing error):
# if "const" in schema:

# Fixed:
if isinstance(schema.get("const"), (list, dict, str, int, float)):
    return "const"
```

**Why**: Gradio was checking if "const" exists in schema, but when schema["const"] is a boolean, the `in` operator fails.

### Import and Path Issues

**Issue**: WebUI Importing Wrong Config Module

**Error Message**:
```
ImportError: cannot import name 'GPU_INDEX' from 'config'
```

**Root Cause**: `webui.py` was importing the root project's `config` package instead of its local `config.py`

**Solution**: Modified `models/GPT-SoVITS/webui.py`:
```python
import os
now_dir = os.getcwd()
os.chdir(os.path.dirname(__file__))  # Change to webui.py's directory BEFORE imports

from config import python_exec, infer_device, is_half
# ... rest of imports
```

### Data Preparation Best Practices

#### 1. File Paths in Training Lists

**Issue**: Confusion between absolute vs relative paths in `.list` files

**What works**: Use relative paths from the GPT-SoVITS directory:
```
dataset\tars\sliced\0001.wav_0000000000_0000390080.wav|sliced|EN|Transcription text here
```

**WebUI fields**:
- **Text labelling file**: `dataset\tars\asr_output\sliced.list`
- **Audio dataset folder**: `dataset\tars\sliced`

**Why**: The training scripts only use the basename of audio files anyway, but relative paths keep things clean and portable.

#### 2. Speech Slicing Parameters

**Settings that worked well**:
- Minimum audio duration: 2 seconds
- Maximum audio duration: 12 seconds
- Language: Leave as default for auto-detect

#### 3. ASR (Speech Recognition) Output

**Important**: The ASR tool creates `sliced.list` in the `asr_output` folder. This is the file you'll use for training, NOT the original audio file list.

**Format**: `audio_path|speaker_name|language|transcription`

#### 4. Proofreading Transcriptions

**Critical step**: Always proofread and correct ASR transcriptions before training
- ASR makes mistakes, especially with proper nouns, technical terms, and character names
- Poor transcriptions = poor voice quality
- Use the "1A-Speech-to-Text Proofreading Tool" in the WebUI

### Common Mistakes to Avoid

1. **Don't use Windows Store Python** - Use python.org installer
2. **Don't skip NLTK downloads** - Required for English text processing
3. **Don't skip proofreading** - Bad transcriptions = bad voice quality
4. **Don't use absolute paths** - Use relative paths from GPT-SoVITS directory
5. **Don't forget to activate venv** - Always use `venv310\Scripts\python.exe`
6. **Don't skip port cleanup** - Kill old Python processes before restarting WebUI
7. **Don't ignore PyTorch version** - Must be 2.6+ for security reasons

### Poor Voice Quality

1. **Use more training data**: 10-15 minutes of clean audio
2. **Train for more epochs**: Increase `--epochs` parameter
3. **Check audio quality**: Ensure training audio is clean and clear
4. **Verify transcripts**: Check that transcripts match audio content

### CUDA Out of Memory

Reduce batch size:
```bash
# In WebUI, reduce batch size from 4 to 2 or 1
```

---

## After Training

### Testing Your Model

Once training is complete, you can test your model in the **Inference** tab:
1. Select your trained GPT and SoVITS models
2. Upload a reference audio (one of your training clips)
3. Enter text for TARS to speak
4. Generate and listen to the output

### Export to ONNX

For deployment, export models to ONNX format:

```bash
python scripts/export_onnx.py --model-dir models/gptsovits_models/tars_voice --quantize
```

This creates:
- `tars_gpt_fp32.onnx` - GPT model (FP32)
- `tars_vits_fp32.onnx` - VITS model (FP32)
- `tars_gpt_int8.onnx` - GPT model (INT8, for Pi)
- `tars_vits_int8.onnx` - VITS model (INT8, for Pi)

### Model Configuration

Edit `.env` file to configure GPT-SoVITS:

```bash
# GPT-SoVITS Settings
GPTSOVITS_MODEL_DIR=models/gptsovits_models/tars_voice
GPTSOVITS_USE_ONNX=true
GPTSOVITS_QUANTIZED=false
```

- `GPTSOVITS_USE_ONNX`: Use ONNX models (recommended: true)
- `GPTSOVITS_QUANTIZED`: Use INT8 quantized models (for Pi: true, for workstation: false)

---

## File Structure Reference

```
FromScratchTARS/
├── venv310/                    # Virtual environment (Python 3.10.11)
├── models/
│   └── GPT-SoVITS/
│       ├── webui.py           # Main WebUI launcher
│       ├── dataset/
│       │   └── tars/          # Your training data
│       │       ├── raw/       # Original audio files
│       │       ├── sliced/    # Sliced audio segments
│       │       └── asr_output/
│       │           └── sliced.list  # Training list file
│       ├── logs/
│       │   └── tars/          # Training outputs and checkpoints
│       └── GPT_SoVITS/
│           ├── pretrained_models/  # Required models
│           │   ├── chinese-roberta-wwm-ext-large/
│           │   ├── chinese-hubert-base/
│           │   └── v2Pro/
│           └── prepare_datasets/   # Data processing scripts
```

---

## Performance Benchmarks

### Training Speed
- **RTX 3080 (Windows)**: ~1 minute per epoch
- **M1 Max (macOS)**: ~3 minutes per epoch
- **CPU (i7-12700)**: ~20 minutes per epoch

### Inference Speed
- **ONNX FP32 (GPU)**: ~50-100ms per sentence
- **ONNX INT8 (CPU)**: ~200-400ms per sentence
- **PyTorch (GPU)**: ~100-200ms per sentence

---

## Success Indicators

You know everything is working when:
- ✅ WebUI loads at `http://127.0.0.1:9874` without errors
- ✅ Speech slicing completes and generates files in `sliced/` folder
- ✅ ASR generates `sliced.list` with transcriptions
- ✅ Proofreading tool opens without "no API found" error
- ✅ Tokenization completes without NLTK errors
- ✅ All three feature extraction steps complete successfully
- ✅ Training logs show decreasing loss values

---

## Quick Reference Commands

### Running WebUI
```bash
cd models\GPT-SoVITS
..\..\venv310\Scripts\python.exe webui.py
```

### Troubleshooting
```bash
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Check port usage
netstat -ano | findstr :9874

# Check Python version
python --version  # Should be 3.10.11

# Check PyTorch version
python -c "import torch; print(torch.__version__)"  # Should be 2.6.0+
```

---

## Support Resources

- **GPT-SoVITS GitHub**: https://github.com/RVC-Boss/GPT-SoVITS
- **FFmpeg**: https://ffmpeg.org/
- **Python 3.10.11**: https://www.python.org/downloads/release/python-31011/
- **PyTorch Installation**: https://pytorch.org/get-started/locally/
- **NLTK Data**: https://www.nltk.org/data.html

---

*Last updated: December 26, 2025*
*Based on real troubleshooting session with TARS voice model training*

