"""Platform detection utilities for Windows vs Raspberry Pi."""

import platform
import os


def is_raspberry_pi():
    """Detect if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except (IOError, FileNotFoundError):
        return False


def is_windows():
    """Detect if running on Windows."""
    return platform.system() == 'Windows'


def get_platform():
    """Get current platform identifier."""
    if is_raspberry_pi():
        return 'raspberry_pi'
    elif is_windows():
        return 'windows'
    else:
        return 'linux'


def get_whisper_model():
    """Get appropriate Whisper model for current platform."""
    platform_type = get_platform()
    
    if platform_type == 'raspberry_pi':
        # Check Pi version for optimization
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Pi 5' in cpuinfo:
                    return 'base.int8'  # Pi 5 can handle base
                else:
                    return 'tiny.int8'  # Pi 4 uses tiny
        except:
            return 'tiny.int8'  # Default to smallest
    else:
        return 'medium'  # Windows can handle medium model


def get_tts_config():
    """Get TTS configuration for current platform."""
    platform_type = get_platform()
    
    if platform_type == 'raspberry_pi':
        return {
            'engine': 'realtimetts',
            'backend': 'system',  # Lightweight system TTS
            'model': None  # No heavy models on Pi
        }
    else:
        return {
            'engine': 'realtimetts',
            'backend': 'cosyvoice2',  # Full CosyVoice2 on Windows
            'model': 'cosyvoice2-0.5b'
        }





