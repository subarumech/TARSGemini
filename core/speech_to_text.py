"""Speech-to-text using faster-whisper."""

import sounddevice as sd
import numpy as np
from typing import Optional, Callable
from faster_whisper import WhisperModel
from config.settings import WHISPER_MODEL, MODELS_DIR


class SpeechToText:
    """Speech recognition using faster-whisper."""
    
    def __init__(self, model_size: Optional[str] = None, 
                 device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda)
            compute_type: Compute type (int8, float16, float32)
        """
        self.model_size = model_size or WHISPER_MODEL
        self.device = device
        self.compute_type = compute_type
        
        # Initialize model
        print(f"Loading Whisper model: {self.model_size}...")
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
            download_root=str(MODELS_DIR)
        )
        print("Whisper model loaded!")
    
    def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        segments, info = self.model.transcribe(
            audio_data,
            language="en",
            beam_size=5,
            vad_filter=True
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    def transcribe_file(self, audio_file: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        segments, info = self.model.transcribe(
            audio_file,
            language="en",
            beam_size=5,
            vad_filter=True
        )
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    def transcribe_stream(self, audio_chunk: np.ndarray, 
                         sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe audio chunk (for streaming).
        
        Args:
            audio_chunk: Audio chunk as numpy array
            sample_rate: Sample rate
            
        Returns:
            Transcribed text or None if not enough audio
        """
        try:
            segments, info = self.model.transcribe(
                audio_chunk,
                language="en",
                beam_size=3,
                vad_filter=True,
                condition_on_previous_text=False
            )
            
            segments_list = list(segments)
            if segments_list:
                return " ".join([seg.text for seg in segments_list])
            return None
        except Exception:
            return None
    
    def record_audio(self, duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate
            
        Returns:
            Audio data as numpy array
        """
        print(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        return audio.flatten()

