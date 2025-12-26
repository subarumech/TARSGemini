# Raspberry Pi Deployment Guide

## Overview

This guide covers deploying GPT-SoVITS models to a Raspberry Pi for low-latency, on-device TTS inference.

## Prerequisites

1. **Trained Models**: Complete training on Windows/Mac workstation (see `GPTSOVITS_SETUP.md`)
2. **ONNX Export**: Export models with INT8 quantization:
   ```bash
   python scripts/export_onnx.py --model-dir models/gptsovits_models/tars_voice --quantize
   ```
3. **Raspberry Pi**: Pi 4 (4GB+) or Pi 5 recommended

## Step 1: Transfer Models to Pi

Copy the INT8 quantized ONNX models to your Raspberry Pi:

```bash
# From workstation
scp models/gptsovits_models/tars_voice/onnx/tars_gpt_int8.onnx pi@raspberrypi.local:~/tars_models/
scp models/gptsovits_models/tars_voice/onnx/tars_vits_int8.onnx pi@raspberrypi.local:~/tars_models/
```

Or use USB drive, SCP, or any file transfer method.

## Step 2: Install Dependencies on Pi

SSH into your Raspberry Pi:

```bash
ssh pi@raspberrypi.local
```

Install Python dependencies:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y python3-pip python3-venv portaudio19-dev

# Install ONNX Runtime for ARM
pip3 install onnxruntime

# Install other dependencies
pip3 install numpy soundfile librosa
```

## Step 3: Run Inference Server

Copy the inference server script to your Pi:

```bash
# From Pi
cd ~/tars_models
# Copy scripts/pi_inference_server.py here
```

Start the server:

```bash
python3 pi_inference_server.py --model-dir ~/tars_models --port 8000
```

The server will:
- Load INT8 quantized ONNX models
- Accept text via HTTP POST
- Return audio as WAV file
- Optimize for low memory usage

## Step 4: Connect Main Application

Update your main application to use the Pi inference server:

```python
# In .env or config
GPTSOVITS_PI_SERVER=http://raspberrypi.local:8000
```

Or modify `core/gptsovits_tts.py` to support remote inference.

## Performance Optimization

### Memory Optimization

The Pi has limited RAM. To reduce memory usage:

1. **Use INT8 models**: Already done (4x smaller than FP32)
2. **Limit batch size**: Process one sentence at a time
3. **Clear cache**: Restart server periodically if memory leaks

### Latency Optimization

To reduce "Time to First Byte":

1. **Preload models**: Models are loaded at server startup
2. **Keep server running**: Don't restart between requests
3. **Use local network**: Ensure Pi is on same network as workstation
4. **Optimize preprocessing**: Minimize text processing overhead

### CPU Optimization

1. **Use Pi 5**: Significantly faster than Pi 4
2. **Overclock**: Can improve inference speed (with proper cooling)
3. **Disable unnecessary services**: Free up CPU resources

## Expected Performance

### Raspberry Pi 5
- **Model Loading**: ~5-10 seconds (one-time at startup)
- **Inference**: ~300-500ms per sentence
- **Memory Usage**: ~500MB-1GB

### Raspberry Pi 4
- **Model Loading**: ~10-20 seconds (one-time at startup)
- **Inference**: ~500-1000ms per sentence
- **Memory Usage**: ~500MB-1GB

## Troubleshooting

### "Out of memory"

- Use INT8 models (already done)
- Close other applications
- Consider using Pi 5 or more RAM

### "Slow inference"

- Check CPU usage: `top`
- Ensure models are INT8 quantized
- Consider overclocking (with cooling)

### "Connection refused"

- Check server is running: `ps aux | grep pi_inference_server`
- Verify firewall allows port 8000
- Check network connectivity

### "Model loading failed"

- Verify ONNX files are present
- Check file permissions
- Ensure onnxruntime is installed correctly

## Alternative: Direct Integration

Instead of using a separate server, you can integrate ONNX inference directly into the main application:

1. Copy ONNX models to Pi's `models/gptsovits_models/tars_voice/onnx/`
2. Set `GPTSOVITS_USE_ONNX=true` and `GPTSOVITS_QUANTIZED=true` in `.env`
3. Run `python main.py` directly on Pi

This eliminates network latency but requires running the full application on Pi.

## Future Improvements

- **Model distillation**: Create even smaller models specifically for Pi
- **Piper TTS integration**: Alternative TTS optimized for Pi
- **Hardware acceleration**: Use Pi's GPU if available
- **Streaming**: Stream audio chunks as they're generated

## Resources

- [ONNX Runtime ARM Builds](https://github.com/microsoft/onnxruntime/releases)
- [Raspberry Pi Performance Tuning](https://www.raspberrypi.com/documentation/computers/config_txt.html)

