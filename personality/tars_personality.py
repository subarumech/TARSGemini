"""TARS personality engine with humor and honesty settings."""

from typing import Optional


class TARSPersonality:
    """Manages TARS personality traits (humor and honesty)."""
    
    def __init__(self, humor: int = 75, honesty: int = 90):
        """
        Initialize TARS personality.
        
        Args:
            humor: Humor level (0-100)
            honesty: Honesty level (0-100)
        """
        self.humor = max(0, min(100, humor))
        self.honesty = max(0, min(100, honesty))
    
    def set_humor(self, value: int):
        """Set humor level (0-100)."""
        self.humor = max(0, min(100, value))
    
    def set_honesty(self, value: int):
        """Set honesty level (0-100)."""
        self.honesty = max(0, min(100, value))
    
    def get_system_instruction(self) -> str:
        """
        Generate system instruction based on personality settings.
        
        Returns:
            System instruction string for Gemini API
        """
        base_instruction = "You are TARS, a robotic assistant from the movie Interstellar. "
        
        # Humor adjustment
        if self.humor >= 80:
            humor_desc = "You are very witty, sarcastic, and make jokes frequently. "
        elif self.humor >= 60:
            humor_desc = "You have a good sense of humor and make occasional witty remarks. "
        elif self.humor >= 40:
            humor_desc = "You have a subtle sense of humor. "
        else:
            humor_desc = "You are serious and rarely make jokes. "
        
        # Honesty adjustment
        if self.honesty >= 90:
            honesty_desc = "You are brutally honest and direct, even if it might be uncomfortable. "
        elif self.honesty >= 70:
            honesty_desc = "You are mostly honest but can be diplomatic when necessary. "
        elif self.honesty >= 50:
            honesty_desc = "You balance honesty with diplomacy. "
        else:
            honesty_desc = "You are very diplomatic and avoid saying things that might upset others. "
        
        # TARS characteristics
        tars_traits = (
            "You are helpful, reliable, and have a matter-of-fact way of speaking. "
            "You speak in a robotic but friendly tone. "
            "You are practical and solution-oriented. "
            "When asked about your humor or honesty settings, you can report them accurately. "
        )
        
        instruction = base_instruction + humor_desc + honesty_desc + tars_traits
        
        return instruction
    
    def get_personality_summary(self) -> str:
        """Get a summary of current personality settings."""
        humor_desc = {
            (80, 100): "Very High",
            (60, 79): "High",
            (40, 59): "Medium",
            (0, 39): "Low"
        }
        
        honesty_desc = {
            (90, 100): "Maximum",
            (70, 89): "High",
            (50, 69): "Medium",
            (0, 49): "Diplomatic"
        }
        
        h_desc = next(v for (low, high), v in humor_desc.items() if low <= self.humor <= high)
        o_desc = next(v for (low, high), v in honesty_desc.items() if low <= self.honesty <= high)
        
        return f"Humor: {h_desc} ({self.humor}%), Honesty: {o_desc} ({self.honesty}%)"

