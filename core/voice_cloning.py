"""Voice cloning using RVC (Retrieval-based Voice Conversion) for TARS voice."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from config.settings import MODELS_DIR, AUDIO_CACHE_DIR, RVC_MODEL_PATH, BASE_TTS_ENGINE


class VoiceCloning:
    """Voice cloning engine using RVC + base TTS."""
    
    def __init__(self, rvc_model_path: Optional[str] = None, base_tts_engine: Optional[str] = None):
        """
        Initialize voice cloning engine.
        
        Args:
            rvc_model_path: Path to RVC model file (.pth)
            base_tts_engine: Base TTS engine to use ('edge-tts', 'gtts', or 'pyttsx3')
        """
        self.rvc_model_path = rvc_model_path or RVC_MODEL_PATH
        self.base_tts_engine = base_tts_engine or BASE_TTS_ENGINE
        self.rvc = None
        self.base_tts = None
        self.model_loaded = False
        self._init_components()
    
    def _init_components(self):
        """Initialize RVC and base TTS components."""
        try:
            from core.rvc_cloning import RVCCloning
            from core.base_tts import BaseTTS
            
            # Initialize base TTS
            print(f"Initializing base TTS: {self.base_tts_engine}")
            self.base_tts = BaseTTS(self.base_tts_engine)
            if not self.base_tts.is_available():
                print("ERROR: Base TTS not available")
                sys.exit(1)
            
            # Initialize RVC model
            print(f"Loading RVC model: {self.rvc_model_path}")
            self.rvc = RVCCloning(self.rvc_model_path)
            if not self.rvc.is_available():
                print("ERROR: RVC model not available")
                sys.exit(1)
            
            self.model_loaded = True
            print("Voice cloning initialized successfully!")
            
        except ImportError as e:
            print(f"ERROR: Failed to import required modules: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize voice cloning: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def clone_voice(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate speech using cloned voice via RVC pipeline.
        
        Pipeline: Text -> Base TTS -> RVC Conversion -> TARS Voice
        
        Args:
            text: Text to speak
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.model_loaded or not self.base_tts or not self.rvc:
            return None
        
        try:
            # Generate output path if not provided
            if not output_path:
                # Create cache directory if it doesn't exist
                AUDIO_CACHE_DIR.mkdir(exist_ok=True)
                # Use hash of text for filename
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = str(AUDIO_CACHE_DIR / f"tts_{text_hash}.wav")
            
            # Step 1: Generate speech with base TTS
            temp_audio = self.base_tts.synthesize(text)
            if not temp_audio or not os.path.exists(temp_audio):
                print("Error: Base TTS failed to generate audio")
                return None
            
            # Step 2: Convert to TARS voice using RVC
            converted_audio = self.rvc.convert(temp_audio, output_path)
            
            # Clean up temporary file
            if temp_audio != output_path and os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass
            
            if converted_audio and os.path.exists(converted_audio):
                return converted_audio
            else:
                print("Error: RVC conversion failed")
                return None
            
        except Exception as e:
            print(f"Error cloning voice: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Check if voice cloning is available."""
        return (self.model_loaded and 
                self.base_tts is not None and 
                self.rvc is not None and
                self.base_tts.is_available() and
                self.rvc.is_available())

