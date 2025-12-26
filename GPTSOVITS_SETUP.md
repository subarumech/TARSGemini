# GPT-SoVITS Voice Cloning Setup Guide

## Overview

GPT-SoVITS is a high-quality text-to-speech system that uses a two-stage architecture:
1. **GPT Model (Stage 1)**: Generates prosody and rhythm from text
2. **VITS Model (Stage 2)**: Synthesizes high-quality waveform audio

This guide covers training a custom TARS voice model on Windows or Mac and preparing it for deployment.

## System Requirements

### Windows (NVIDIA GPU Recommended)
- Windows 10/11
- NVIDIA GPU with CUDA support (6GB+ VRAM recommended)
- Python 3.9+
- 10GB+ free disk space

### macOS (Apple Silicon Recommended)
- macOS 11+ (Big Sur or later)
- Apple Silicon (M1/M2/M3) for MPS acceleration
- Python 3.9+
- 10GB+ free disk space

### CPU-Only (Not Recommended)
- Training will be very slow (4-6 hours)
- Inference is acceptable but slower than GPU

## Quick Start

### Step 1: Setup GPT-SoVITS

```bash
python scripts/setup_gptsovits.py
```

This will:
- Clone the GPT-SoVITS repository
- Install platform-specific PyTorch (CUDA/MPS/CPU)
- Install all required dependencies
- Verify installation

### Step 2: Prepare Training Data

```bash
python scripts/prepare_training_data.py --audio voice_samples/tars_sample.wav
```

This will:
- Convert audio to 32kHz mono WAV format
- Split long files into segments (if needed)
- Generate transcripts using Whisper ASR
- Create dataset structure for GPT-SoVITS

**Audio Requirements**:
- Minimum: 3 minutes of clean audio
- Recommended: 5-15 minutes
- Format: WAV, MP3, or other common formats
- Quality: Clear speech, minimal background noise

### Step 3: Train Model

```bash
python scripts/train_gptsovits.py --dataset models/GPT-SoVITS/dataset/tars
```

**Training Time Estimates**:
- Windows (RTX 3080): ~30 minutes for 30 epochs
- Mac M1: ~1-2 hours for 20 epochs
- CPU Only: ~4-6 hours for 10 epochs (not recommended)

The script automatically detects your hardware and adjusts training parameters:
- **Windows GPU**: batch_size=4, epochs=30
- **Mac MPS**: batch_size=2, epochs=20
- **CPU**: batch_size=1, epochs=10 (with warning)

### Step 4: Export to ONNX

```bash
python scripts/export_onnx.py --model-dir models/gptsovits_models/tars_voice --quantize
```

This creates:
- `tars_gpt_fp32.onnx` - GPT model (FP32)
- `tars_vits_fp32.onnx` - VITS model (FP32)
- `tars_gpt_int8.onnx` - GPT model (INT8, for Pi)
- `tars_vits_int8.onnx` - VITS model (INT8, for Pi)

### Step 5: Test in Application

```bash
python main.py
```

The application will automatically use GPT-SoVITS models if they're properly configured.

## Detailed Setup Instructions

### Manual Setup (Alternative)

If automated setup fails, you can set up GPT-SoVITS manually:

1. **Clone Repository**:
   ```bash
   cd models
   git clone https://github.com/RVC-Boss/GPT-SoVITS.git
   cd GPT-SoVITS
   ```

2. **Install PyTorch** (platform-specific):
   
   Windows (CUDA):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   
   macOS (MPS):
   ```bash
   pip install torch torchvision torchaudio
   ```
   
   CPU Only:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install librosa soundfile audioread cn2an jieba onnx onnxruntime ffmpeg-python
   ```

### Training Parameters

You can customize training by editing `scripts/train_gptsovits.py` or passing arguments:

```bash
python scripts/train_gptsovits.py \
    --dataset models/GPT-SoVITS/dataset/tars \
    --batch-size 4 \
    --epochs 30
```

**Key Parameters**:
- `--batch-size`: Larger = faster training but more VRAM (default: auto-detected)
- `--epochs`: More epochs = better quality but longer training (default: auto-detected)
- `--dataset`: Path to prepared dataset directory

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

## Troubleshooting

### "GPT-SoVITS not found"

Run setup script:
```bash
python scripts/setup_gptsovits.py
```

### "CUDA out of memory"

Reduce batch size:
```bash
python scripts/train_gptsovits.py --dataset ... --batch-size 2
```

### "ONNX models not found"

Export models:
```bash
python scripts/export_onnx.py --model-dir models/gptsovits_models/tars_voice
```

### "Training script not found"

GPT-SoVITS repository structure may have changed. Check:
```bash
ls models/GPT-SoVITS/
```

Look for training scripts like `train_s1.py`, `train_s2.py`, or check the `api/` directory.

### Poor Voice Quality

1. **Use more training data**: 10-15 minutes of clean audio
2. **Train for more epochs**: Increase `--epochs` parameter
3. **Check audio quality**: Ensure training audio is clean and clear
4. **Verify transcripts**: Check that transcripts match audio content

### Slow Inference

1. **Use ONNX models**: Faster than PyTorch
2. **Use INT8 quantization**: Smaller and faster (slight quality trade-off)
3. **Check GPU availability**: Ensure CUDA/MPS is working

## Performance Benchmarks

### Training Speed
- **RTX 3080 (Windows)**: ~1 minute per epoch
- **M1 Max (macOS)**: ~3 minutes per epoch
- **CPU (i7-12700)**: ~20 minutes per epoch

### Inference Speed
- **ONNX FP32 (GPU)**: ~50-100ms per sentence
- **ONNX INT8 (CPU)**: ~200-400ms per sentence
- **PyTorch (GPU)**: ~100-200ms per sentence

## Next Steps

After training:
1. Test voice quality with various texts
2. Export ONNX models for deployment
3. For Raspberry Pi: Use INT8 quantized models (see `PI_DEPLOYMENT.md`)

## Resources

- [GPT-SoVITS GitHub](https://github.com/RVC-Boss/GPT-SoVITS)
- [GPT-SoVITS Documentation](https://github.com/RVC-Boss/GPT-SoVITS/wiki)
- [ONNX Runtime Documentation](https://onnxruntime.ai/docs/)

## Migration from RVC

If you were using RVC before:
1. Your `tars_sample.wav` can be reused
2. RVC models are no longer needed
3. GPT-SoVITS provides better quality and direct text-to-speech (no base TTS needed)

