"""Text-to-speech using GPT-SoVITS voice cloning - mandatory, no fallback."""

import threading
import queue
import os
import sys
from typing import Optional, Callable
from config.settings import USE_VOICE_CLONING, TARS_VOICE_SAMPLE
import time


class TextToSpeech:
    """Text-to-speech engine using mandatory voice cloning."""
    
    def __init__(self):
        """Initialize TTS engine with mandatory voice cloning."""
        self.voice_cloning = None
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.speech_thread = None
        self._worker_running = False
        
        # Mandatory validation - exit if voice cloning cannot be initialized
        self._validate_voice_cloning_required()
        self._init_voice_cloning()
        self._test_voice_generation()
    
    def _validate_voice_cloning_required(self):
        """Validate that voice cloning is required and configured."""
        # Note: Basic file existence check happens in settings.py
        # This method is kept for consistency but validation already occurred
        if not USE_VOICE_CLONING:
            print("ERROR: Voice cloning is required but USE_VOICE_CLONING=false")
            print("Please set USE_VOICE_CLONING=true in your .env file")
            sys.exit(1)
    
    def _init_voice_cloning(self):
        """Initialize voice cloning - mandatory, exits on failure."""
        try:
            from core.voice_cloning import VoiceCloning
            
            self.voice_cloning = VoiceCloning()
            if not self.voice_cloning.is_available():
                print("ERROR: Voice cloning initialized but not available")
                print("Check that GPT-SoVITS models exist and are properly configured")
                print("Install dependencies: pip install -r requirements-windows.txt")
                print("Train model: See GPTSOVITS_SETUP.md for instructions")
                sys.exit(1)
            
            print("Voice cloning initialized successfully with GPT-SoVITS")
        except ImportError:
            print("ERROR: GPT-SoVITS dependencies not installed")
            print("Install with: pip install -r requirements-windows.txt")
            print("Required: torch, torchaudio, librosa, soundfile, onnxruntime")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize voice cloning: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _test_voice_generation(self):
        """Test voice generation on startup to ensure it works."""
        print("Testing voice generation...")
        try:
            test_text = "TARS voice ready."
            audio_file = self.voice_cloning.clone_voice(test_text)
            if audio_file and os.path.exists(audio_file):
                print("Voice cloning test successful!")
                print("TARS voice ready.")
            else:
                print("ERROR: Voice generation test failed - no audio file generated")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Voice generation test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def speak(self, text: str, callback: Optional[Callable] = None):
        """
        Speak text synchronously using voice cloning.
        
        Args:
            text: Text to speak
            callback: Optional callback when speech completes
        """
        if not text or not text.strip():
            if callback:
                callback()
            return
        
        if not self.voice_cloning:
            print("ERROR: Voice cloning not available")
            if callback:
                callback()
            return
        
        try:
            audio_file = self.voice_cloning.clone_voice(text)
            if audio_file and os.path.exists(audio_file):
                self._play_audio_file(audio_file, callback)
            else:
                print(f"ERROR: Failed to generate audio for text: {text[:50]}...")
                if callback:
                    callback()
        except Exception as e:
            print(f"ERROR: Voice cloning failed: {e}")
            import traceback
            traceback.print_exc()
            if callback:
                callback()
    
    def _play_audio_file(self, audio_file: str, callback: Optional[Callable] = None):
        """
        Play an audio file.
        
        Args:
            audio_file: Path to audio file
            callback: Optional callback when playback completes
        """
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            self.is_speaking = True
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.is_speaking = False
            
            if callback:
                callback()
        except ImportError:
            # Fallback to using system player
            import subprocess
            import platform
            
            self.is_speaking = True
            if platform.system() == 'Windows':
                subprocess.run(['start', audio_file], shell=True, check=False)
            elif platform.system() == 'Darwin':
                subprocess.run(['afplay', audio_file], check=False)
            else:
                subprocess.run(['aplay', audio_file], check=False)
            
            # Note: Can't easily detect when playback finishes with subprocess
            # So we'll just mark as not speaking after a delay
            time.sleep(2)  # Rough estimate
            self.is_speaking = False
            
            if callback:
                callback()
        except Exception as e:
            print(f"Error playing audio file: {e}")
            self.is_speaking = False
            if callback:
                callback()
    
    def _speak_queue_worker(self):
        """Worker thread that processes the speech queue sequentially."""
        self._worker_running = True
        print("TTS queue worker started")
        
        while self._worker_running:
            try:
                # Get next item from queue (blocks until available)
                try:
                    item = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                if item is None:  # Sentinel to stop
                    self.audio_queue.task_done()
                    break
                
                text, callback = item
                if text and text.strip():  # Only speak if text is not empty
                    print(f"TTS queue processing: {text[:60]}...")
                    self.speak(text.strip(), callback)
                    print(f"TTS queue completed: {text[:60]}...")
                self.audio_queue.task_done()
            except Exception as e:
                print(f"TTS queue worker error: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("TTS queue worker stopped")
        self._worker_running = False
    
    def speak_async(self, text: str, callback: Optional[Callable] = None):
        """
        Speak text asynchronously (queued).
        
        Args:
            text: Text to speak
            callback: Optional callback when speech completes
        """
        if not self.voice_cloning:
            print("ERROR: Voice cloning not available")
            if callback:
                callback()
            return
        
        if not text or not text.strip():
            return
        
        # Start queue worker if not running
        if not self._worker_running or not self.speech_thread or not self.speech_thread.is_alive():
            self._worker_running = True
            self.speech_thread = threading.Thread(
                target=self._speak_queue_worker,
                daemon=True
            )
            self.speech_thread.start()
            # Give it a moment to start
            time.sleep(0.1)
        
        # Add to queue (will be processed sequentially)
        self.audio_queue.put((text.strip(), callback))
    
    def stop(self):
        """Stop current speech and clear queue."""
        self.is_speaking = False
        
        # Clear queue (don't stop worker - we want it to keep running)
        cleared = 0
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
                cleared += 1
            except:
                break
        if cleared > 0:
            print(f"Cleared {cleared} items from TTS queue")

