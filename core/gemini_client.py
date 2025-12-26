"""Gemini API client with streaming support."""

import google.generativeai as genai
from typing import Iterator, Optional, List, Dict
from config.settings import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    """Client for interacting with Google Gemini API with streaming."""
    
    def __init__(self, system_instruction: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            system_instruction: Optional system instruction for personality
        """
        genai.configure(api_key=GEMINI_API_KEY)
        # Create model with system instruction if provided
        if system_instruction:
            self.model = genai.GenerativeModel(
                GEMINI_MODEL,
                system_instruction=system_instruction
            )
        else:
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.conversation_history: List[Dict] = []
        self._system_instruction = system_instruction
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            'role': role,
            'parts': [content]
        })
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def update_system_instruction(self, system_instruction: str):
        """
        Update system instruction by recreating the model.
        
        Args:
            system_instruction: New system instruction
        """
        if system_instruction != self._system_instruction:
            self.model = genai.GenerativeModel(
                GEMINI_MODEL,
                system_instruction=system_instruction
            )
            self._system_instruction = system_instruction
    
    def generate_stream(self, prompt: str) -> Iterator[str]:
        """
        Generate streaming response from Gemini.
        
        Args:
            prompt: User's input prompt
            
        Yields:
            Text chunks as they arrive from the API
        """
        try:
            # Prepare generation config for streaming
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
            
            # Build messages with history
            messages = self.conversation_history.copy()
            messages.append({
                'role': 'user',
                'parts': [prompt]
            })
            
            # Generate with streaming
            response = self.model.generate_content(
                messages,
                generation_config=generation_config,
                stream=True
            )
            
            # Stream chunks
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            
            # Add user message and response to history
            self.add_to_history('user', prompt)
            full_response = ''.join([chunk.text for chunk in response if chunk.text])
            self.add_to_history('model', full_response)
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate non-streaming response (for caching).
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Complete response text
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
            
            messages = self.conversation_history.copy()
            messages.append({
                'role': 'user',
                'parts': [prompt]
            })
            
            response = self.model.generate_content(
                messages,
                generation_config=generation_config
            )
            
            result = response.text
            
            # Add to history
            self.add_to_history('user', prompt)
            self.add_to_history('model', result)
            
            return result
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def set_conversation_history(self, history: List[Dict]):
        """Set conversation history from external source."""
        self.conversation_history = history

