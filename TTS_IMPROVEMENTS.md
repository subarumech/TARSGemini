# TTS Voice Quality Improvements

## Current Status

The application uses `pyttsx3` which provides basic TTS functionality but has limited voice quality. The current implementation:
- Uses Windows SAPI5 voices (David, Zira, Mark)
- Adjusts rate and volume for a more robotic feel
- Processes sentences sequentially

## Better TTS Options

### Option 1: Windows SAPI5 Direct (Better Quality)
Windows has better voices available through SAPI5. You can install additional voices:
- **Microsoft David** (default male) - deeper, more robotic
- **Microsoft Zira** (default female)
- **Microsoft Mark** (alternative male)

To improve voice quality:
1. Go to Windows Settings > Time & Language > Speech
2. Install additional voices if available
3. The app will automatically detect and use them

### Option 2: ElevenLabs API (Best Quality, Requires API Key)
- High-quality, natural-sounding voices
- Can clone TARS voice from movie samples
- Requires API key and internet connection
- Cost: ~$5/month for basic usage

### Option 3: Coqui TTS (Open Source, Better than pyttsx3)
- Free, open-source
- Better quality than pyttsx3
- Can run locally
- Requires: `pip install TTS`

### Option 4: Piper TTS (Lightweight, Good Quality)
- Fast, lightweight neural TTS
- Good quality for local use
- Works on Windows and Raspberry Pi
- Requires: Download Piper binaries

## Quick Fix: Improve Current Voice

The current implementation now:
- Prefers male voices (David, Mark)
- Uses slower rate (140 WPM) for more robotic feel
- Attempts to lower pitch if supported

To manually select a better voice, check the console output when the app starts - it will list all available voices.

## Recommended Next Steps

1. **Short term**: Use current pyttsx3 with improved voice selection (already implemented)
2. **Medium term**: Integrate Coqui TTS or Piper for better quality
3. **Long term**: Use ElevenLabs for TARS voice cloning

## Testing Voice Quality

Run the app and check the console output:
```
Available voices:
  0: Microsoft David Desktop - English (United States)
  1: Microsoft Zira Desktop - English (United States)
Selected voice: Microsoft David Desktop
```

If you see a different voice selected, you can modify `core/text_to_speech.py` to prefer a specific voice by name.

