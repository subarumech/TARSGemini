"""Setup script for Raspberry Pi deployment."""

import os
import sys
from pathlib import Path

def main():
    """Run Pi-specific setup."""
    print("TARS AI Assistant - Raspberry Pi Setup")
    print("=" * 40)
    
    # Check if running on Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' not in cpuinfo:
                print("Warning: This doesn't appear to be a Raspberry Pi")
    except:
        print("Warning: Could not detect Raspberry Pi")
    
    print("\n1. Installing system dependencies...")
    os.system("sudo apt-get update")
    os.system("sudo apt-get install -y python3-pyaudio portaudio19-dev python3-pyqt5")
    
    print("\n2. Downloading Whisper models...")
    print("   This will download the quantized tiny model (~75MB)")
    print("   Run this manually: python -c 'from faster_whisper import WhisperModel; WhisperModel(\"tiny.int8\")'")
    
    print("\n3. Setup complete!")
    print("\nNext steps:")
    print("  - Create .env file with your GEMINI_API_KEY")
    print("  - Run: python main.py")

if __name__ == "__main__":
    main()





