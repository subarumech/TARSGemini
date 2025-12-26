# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Windows Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/subarumech/TARSGemini.git
   cd TARSGemini
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-windows.txt
   ```

4. **Create .env file**:
   Create a file named `.env` in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   DEFAULT_HUMOR=75
   DEFAULT_HONESTY=90
   SAVE_HISTORY_DEFAULT=false
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## Raspberry Pi Setup

1. **Install system dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pyaudio portaudio19-dev python3-pyqt5
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements-pi.txt
   ```

3. **Create .env file** (same as Windows)

4. **Download Whisper models** (first run will auto-download):
   The first time you run, faster-whisper will download the quantized model (~75MB for tiny.int8)

5. **Run the application**:
   ```bash
   python main.py
   ```

## First Run

On first run, faster-whisper will download the Whisper model. This may take a few minutes depending on your internet connection:
- Windows: Downloads `medium` model (~1.5GB)
- Raspberry Pi: Downloads `tiny.int8` or `base.int8` (~75-150MB)

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created a `.env` file in the project root
- Check that the file is named exactly `.env` (not `.env.txt`)
- Verify your API key is correct

### Audio issues
- Windows: Make sure your microphone is connected and enabled
- Raspberry Pi: Check audio device permissions: `sudo usermod -a -G audio $USER`

### PyQt5 issues
- Windows: Should install automatically with pip
- Raspberry Pi: Install via apt: `sudo apt-get install python3-pyqt5`

### Whisper model download fails
- Check internet connection
- Models are downloaded to `models/` directory
- You can manually download and place models there if needed

