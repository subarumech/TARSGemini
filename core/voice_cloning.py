"""Voice cloning using GPT-SoVITS for TARS voice."""

import os
import sys
from pathlib import Path
from typing import Optional
from config.settings import GPTSOVITS_MODEL_DIR, GPTSOVITS_USE_ONNX, GPTSOVITS_QUANTIZED


class VoiceCloning:
    """Voice cloning engine using GPT-SoVITS."""
    
    def __init__(self, model_dir: Optional[str] = None, use_onnx: Optional[bool] = None, quantized: Optional[bool] = None):
        """
        Initialize voice cloning engine.
        
        Args:
            model_dir: Directory containing GPT-SoVITS model files
            use_onnx: Use ONNX models (default: from config)
            quantized: Use quantized INT8 models (default: from config)
        """
        self.tts_engine = None
        self.model_loaded = False
        self._init_gptsovits(model_dir, use_onnx, quantized)
    
    def _init_gptsovits(self, model_dir: Optional[str], use_onnx: Optional[bool], quantized: Optional[bool]):
        """Initialize GPT-SoVITS TTS engine."""
        try:
            from core.gptsovits_tts import GPTSoVITSTTS
            
            print("Initializing GPT-SoVITS voice cloning...")
            self.tts_engine = GPTSoVITSTTS(model_dir, use_onnx, quantized)
            
            if not self.tts_engine.is_available():
                print("ERROR: GPT-SoVITS not available")
                sys.exit(1)
            
            self.model_loaded = True
            print("Voice cloning initialized successfully with GPT-SoVITS!")
            
        except ImportError as e:
            print(f"ERROR: Failed to import GPT-SoVITS: {e}")
            print("Install dependencies: pip install -r requirements-windows.txt")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize GPT-SoVITS: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def clone_voice(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate speech using cloned voice via GPT-SoVITS.
        
        Pipeline: Text -> GPT-SoVITS -> TARS Voice
        
        Args:
            text: Text to speak
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.model_loaded or not self.tts_engine:
            return None
        
        try:
            # Generate speech directly with GPT-SoVITS
            audio_file = self.tts_engine.synthesize(text, output_path)
            
            if audio_file and os.path.exists(audio_file):
                return audio_file
            else:
                print("Error: GPT-SoVITS synthesis failed")
                return None
            
        except Exception as e:
            print(f"Error cloning voice: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Check if voice cloning is available."""
        return (self.model_loaded and 
                self.tts_engine is not None and
                self.tts_engine.is_available())

