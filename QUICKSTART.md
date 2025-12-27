# Quick Start

## 1. Install Dependencies

```bash
pip install -r requirements-windows.txt
```

## 2. Set Up API Key

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

Get your key from: https://makersuite.google.com/app/apikey

## 3. Run

```bash
python main.py
```

## Features

- **Text Input**: Type your message and press Enter or click Send
- **Personality Sliders**: Adjust humor (0-100%) and honesty (0-100%)
- **Conversation History**: Toggle to save/clear conversation history
- **Geometric Animation**: Watch TARS's blocks animate when speaking

## Microphone Feature

The microphone button is implemented but requires additional setup. Speech recognition will be fully integrated in a future update.

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Make sure `.env` file exists in project root
- **Whisper model download**: First run downloads model (~1.5GB on Windows, ~75MB on Pi)
- **Audio issues**: Check microphone permissions in Windows settings





