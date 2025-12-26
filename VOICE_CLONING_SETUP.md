# Voice Cloning Setup Guide

## Quick Start

1. **Extract TARS audio** from Interstellar movie (see below)
2. **Place WAV file** in `voice_samples/tars_sample.wav`
3. **Enable in .env**: Set `USE_VOICE_CLONING=true`
4. **Install dependencies**: `pip install TTS pygame`
5. **Restart application**

## Step-by-Step Instructions

### Step 1: Extract TARS Audio

You need at least **6 seconds** of clean TARS voice for Coqui XTTS to work.

**Option A: Using FFmpeg (Recommended)**
```bash
# Extract 30 seconds starting at specific time
ffmpeg -i interstellar.mp4 -ss 01:23:45 -t 00:00:30 -vn -acodec pcm_s16le -ar 22050 -ac 1 tars_clip.wav

# Or use the helper script
python scripts/extract_tars_audio.py interstellar.mp4 voice_samples/tars_sample.wav 01:23:45 00:00:30
```

**Option B: Using Audacity (Manual)**
1. Open movie file in Audacity
2. Find TARS dialogue scenes
3. Select and copy TARS-only audio
4. Remove background noise (Effect > Noise Reduction)
5. Export as WAV (File > Export > Export as WAV)
6. Save to `voice_samples/tars_sample.wav`

**Option C: Using Python moviepy**
```python
from moviepy.editor import VideoFileClip
video = VideoFileClip("interstellar.mp4")
audio = video.audio
audio.write_audiofile("tars_sample.wav", fps=22050)
```

### Step 2: Clean the Audio

**Using Audacity:**
1. Open extracted WAV file
2. **Remove noise**: Select a quiet section → Effect > Noise Reduction > Get Noise Profile → Select All → Effect > Noise Reduction > OK
3. **Normalize**: Effect > Normalize
4. **Remove music**: Use Effect > Vocal Reduction and Isolation (if available)
5. Export cleaned version

**Using FFmpeg:**
```bash
# Normalize audio
ffmpeg -i input.wav -af "volume=2.0" output.wav
```

### Step 3: Install Dependencies

```bash
pip install TTS pygame
```

**Note**: Coqui TTS will download ~2GB model on first run. This is normal.

### Step 4: Configure

Edit `.env` file:
```
USE_VOICE_CLONING=true
TARS_VOICE_SAMPLE=voice_samples/tars_sample.wav
```

### Step 5: Test

Run the application:
```bash
python main.py
```

Check console output - you should see:
```
Loading Coqui XTTS model...
Coqui XTTS model loaded successfully!
Voice cloning enabled with TARS voice sample
```

## Troubleshooting

### "Coqui TTS not installed"
```bash
pip install TTS
```

### "TARS voice sample not found"
- Check file path in `.env`
- Ensure file exists at `voice_samples/tars_sample.wav`
- Check file permissions

### "Voice cloning failed, falling back to pyttsx3"
- Check console for error details
- Ensure WAV file is valid (try playing it)
- Try a different audio sample (longer, cleaner)

### Model download is slow
- First run downloads ~2GB model
- This is normal and only happens once
- Model is cached for future use

### Audio quality is poor
- Use longer audio sample (10-30 seconds)
- Clean audio better (remove noise, music)
- Try multiple TARS dialogue clips combined

## Advanced: Using Multiple Samples

For better quality, you can combine multiple TARS clips:

```bash
# Combine multiple clips
ffmpeg -i clip1.wav -i clip2.wav -i clip3.wav -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" -map "[out]" combined.wav
```

## Alternative: RVC (Higher Quality)

If Coqui XTTS doesn't sound good enough, consider RVC:
- Requires 10-30 minutes of audio
- Better quality but more complex setup
- See RVC documentation: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI

## Testing Voice Quality

After setup, test with:
```python
from core.voice_cloning import VoiceCloning
vc = VoiceCloning("voice_samples/tars_sample.wav")
vc.clone_voice("Hello. TARS here. Ready to assist.")
```

Check the generated audio file in `audio_cache/` directory.

