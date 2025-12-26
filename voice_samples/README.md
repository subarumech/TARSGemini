# TARS Voice Samples

Place your TARS voice sample WAV file here.

## Requirements

- **Format**: WAV file (16kHz or 22kHz recommended)
- **Duration**: At least 6 seconds for Coqui XTTS (10-30 minutes for RVC)
- **Quality**: Clean audio with minimal background noise
- **Content**: TARS dialogue from Interstellar movie

## File Name

Name your file `tars_sample.wav` or update the path in `.env`:

```
TARS_VOICE_SAMPLE=voice_samples/your_file.wav
```

## Getting TARS Audio

### Option 1: Extract from Movie
1. Get Interstellar movie file
2. Use Audacity or FFmpeg to extract TARS dialogue scenes
3. Clean audio (remove background music/noise)
4. Export as WAV file

### Option 2: Use Existing Samples
- Check if anyone has shared TARS voice samples online
- Look for fan-made TARS voice clips
- Ensure you have rights to use the audio

### Option 3: Record Your Own
- Record yourself speaking TARS lines
- Use audio effects to make it sound robotic
- This won't be authentic but can work for testing

## Audio Cleaning Tips

1. **Remove background noise**: Use Audacity's noise reduction
2. **Normalize volume**: Ensure consistent levels
3. **Remove music**: Isolate voice-only segments
4. **Split long clips**: Break into 10-30 second segments if needed

## Testing

Once you place the file, enable voice cloning in `.env`:

```
USE_VOICE_CLONING=true
TARS_VOICE_SAMPLE=voice_samples/tars_sample.wav
```

Then restart the application.

