"""Streaming pipeline coordinator for parallel processing."""

import threading
import queue
import re
from typing import Optional, Callable, Iterator
from core.gemini_client import GeminiClient
from core.text_to_speech import TextToSpeech
from core.response_cache import ResponseCache
from personality.tars_personality import TARSPersonality


class StreamingPipeline:
    """Coordinates streaming processing pipeline."""
    
    def __init__(self, gemini_client: GeminiClient, tts: TextToSpeech,
                 personality: TARSPersonality, cache: ResponseCache):
        """
        Initialize streaming pipeline.
        
        Args:
            gemini_client: Gemini API client
            tts: Text-to-speech engine
            personality: TARS personality engine
            cache: Response cache
        """
        self.gemini = gemini_client
        self.tts = tts
        self.personality = personality
        self.cache = cache
        
        self.response_queue = queue.Queue()
        self.sentence_queue = queue.Queue()
        self.is_processing = False
    
    def process_query(self, query: str, on_start: Optional[Callable] = None,
                     on_sentence: Optional[Callable] = None,
                     on_complete: Optional[Callable] = None) -> Iterator[str]:
        """
        Process query through streaming pipeline.
        
        Args:
            query: User query
            on_start: Callback when processing starts
            on_sentence: Callback for each sentence
            on_complete: Callback when processing completes
            
        Yields:
            Response chunks as they arrive
        """
        self.is_processing = True
        
        if on_start:
            on_start()
        
        # Check cache first
        personality_hash = f"{self.personality.humor}_{self.personality.honesty}"
        cached_response = self.cache.get(query, personality_hash)
        
        if cached_response:
            # Return cached response
            if on_sentence:
                on_sentence(cached_response)
            self.tts.speak_async(cached_response, on_complete)
            self.is_processing = False
            yield cached_response
            return
        
        # Update system instruction if personality changed
        system_instruction = self.personality.get_system_instruction()
        self.gemini.update_system_instruction(system_instruction)
        
        # Stream from Gemini
        sentence_buffer = ""
        full_response = ""
        
        # Pattern to match sentence endings: punctuation followed by space or end of string
        # This prevents splitting on abbreviations, decimals, etc.
        sentence_end_pattern = re.compile(r'([.!?])\s+|([.!?])$')
        
        try:
            for chunk in self.gemini.generate_stream(query):
                full_response += chunk
                sentence_buffer += chunk
                
                # Find all sentence endings (punctuation + space or end of string)
                sentences = []
                last_end = 0
                
                # Find all matches
                for match in sentence_end_pattern.finditer(sentence_buffer):
                    # Extract sentence from last_end to match end
                    sentence = sentence_buffer[last_end:match.end()].strip()
                    if sentence:
                        sentences.append(sentence)
                    last_end = match.end()
                
                # Remove processed sentences from buffer
                if sentences:
                    sentence_buffer = sentence_buffer[last_end:]
                
                # Process complete sentences
                for sentence in sentences:
                    # Clean up sentence (remove trailing punctuation if needed)
                    cleaned_sentence = sentence.strip()
                    if cleaned_sentence:
                        yield cleaned_sentence
                        if on_sentence:
                            on_sentence(cleaned_sentence)
                        
                        # Queue sentence for TTS (will be processed sequentially)
                        self.tts.speak_async(cleaned_sentence)
            
            # Process remaining buffer (last sentence without trailing punctuation)
            if sentence_buffer.strip():
                cleaned_remaining = sentence_buffer.strip()
                yield cleaned_remaining
                if on_sentence:
                    on_sentence(cleaned_remaining)
                self.tts.speak_async(cleaned_remaining)
            
            # Cache the response
            self.cache.set(query, full_response, personality_hash)
            
            # Note: Conversation history is managed by GeminiClient internally
            # TTS queue will process all sentences sequentially automatically
            
            if on_complete:
                on_complete()
                
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(error_msg)
            if on_complete:
                on_complete()
            raise
        
        finally:
            self.is_processing = False
    
    def stop(self):
        """Stop current processing."""
        self.tts.stop()
        self.is_processing = False
        
        # Clear queues
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.sentence_queue.empty():
            try:
                self.sentence_queue.get_nowait()
            except queue.Empty:
                break

