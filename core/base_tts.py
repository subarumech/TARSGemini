"""Base TTS engine wrapper for RVC pipeline."""

import os
import sys
import tempfile
from typing import Optional
from pathlib import Path


class BaseTTS:
    """Base TTS engine wrapper for generating speech from text."""
    
    def __init__(self, engine: str = 'edge-tts'):
        """
        Initialize base TTS engine.
        
        Args:
            engine: TTS engine to use ('edge-tts', 'gtts', or 'pyttsx3')
        """
        self.engine_name = engine
        self.tts = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the selected TTS engine."""
        if self.engine_name == 'edge-tts':
            self._init_edge_tts()
        elif self.engine_name == 'gtts':
            self._init_gtts()
        elif self.engine_name == 'pyttsx3':
            self._init_pyttsx3()
        else:
            print(f"ERROR: Unknown TTS engine: {self.engine_name}")
            sys.exit(1)
    
    def _init_edge_tts(self):
        """Initialize Microsoft Edge TTS."""
        try:
            import edge_tts
            self.tts = edge_tts
            print("Base TTS initialized: Microsoft Edge TTS")
        except ImportError:
            print("ERROR: edge-tts not installed")
            print("Install with: pip install edge-tts")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize edge-tts: {e}")
            sys.exit(1)
    
    def _init_gtts(self):
        """Initialize Google TTS."""
        try:
            from gtts import gTTS
            self.tts = gTTS
            print("Base TTS initialized: Google TTS")
        except ImportError:
            print("ERROR: gTTS not installed")
            print("Install with: pip install gtts")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize gTTS: {e}")
            sys.exit(1)
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            print("Base TTS initialized: pyttsx3")
        except ImportError:
            print("ERROR: pyttsx3 not installed")
            print("Install with: pip install pyttsx3")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize pyttsx3: {e}")
            sys.exit(1)
    
    def synthesize(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not text or not text.strip():
            return None
        
        if self.engine_name == 'edge-tts':
            return self._synthesize_edge_tts(text, output_path)
        elif self.engine_name == 'gtts':
            return self._synthesize_gtts(text, output_path)
        elif self.engine_name == 'pyttsx3':
            return self._synthesize_pyttsx3(text, output_path)
        return None
    
    def _synthesize_edge_tts(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Synthesize using Edge TTS."""
        import asyncio
        import edge_tts
        
        if not output_path:
            output_path = tempfile.mktemp(suffix='.mp3')
        
        async def _generate():
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_path)
        
        try:
            asyncio.run(_generate())
            return output_path
        except Exception as e:
            print(f"Error synthesizing with edge-tts: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _synthesize_gtts(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Synthesize using Google TTS."""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.mp3')
        
        try:
            tts = self.tts(text=text, lang='en', slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"Error synthesizing with gTTS: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _synthesize_pyttsx3(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """Synthesize using pyttsx3."""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.wav')
        
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return output_path
        except Exception as e:
            print(f"Error synthesizing with pyttsx3: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Check if TTS engine is available."""
        return self.tts is not None or (hasattr(self, 'engine') and self.engine is not None)

