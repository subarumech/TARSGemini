"""Controls panel for personality settings and conversation management."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                             QCheckBox, QPushButton, QGroupBox)
from PyQt5.QtCore import Qt
from personality.tars_personality import TARSPersonality
from core.conversation_manager import ConversationManager


class ControlsPanel(QWidget):
    """Panel for controlling TARS personality and settings."""
    
    def __init__(self, personality: TARSPersonality, 
                 conversation_manager: ConversationManager,
                 on_change_callback):
        """
        Initialize controls panel.
        
        Args:
            personality: TARS personality instance
            conversation_manager: Conversation manager instance
            on_change_callback: Callback when settings change
        """
        super().__init__()
        self.personality = personality
        self.conversation_manager = conversation_manager
        self.on_change_callback = on_change_callback
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Personality group
        personality_group = QGroupBox("Personality Settings")
        personality_layout = QVBoxLayout()
        
        # Humor slider
        humor_layout = QVBoxLayout()
        humor_layout.addWidget(QLabel("Humor:"))
        self.humor_slider = QSlider(Qt.Horizontal)
        self.humor_slider.setMinimum(0)
        self.humor_slider.setMaximum(100)
        self.humor_slider.setValue(self.personality.humor)
        self.humor_slider.valueChanged.connect(self.on_personality_change)
        humor_layout.addWidget(self.humor_slider)
        self.humor_label = QLabel(f"{self.personality.humor}%")
        humor_layout.addWidget(self.humor_label)
        personality_layout.addLayout(humor_layout)
        
        # Honesty slider
        honesty_layout = QVBoxLayout()
        honesty_layout.addWidget(QLabel("Honesty:"))
        self.honesty_slider = QSlider(Qt.Horizontal)
        self.honesty_slider.setMinimum(0)
        self.honesty_slider.setMaximum(100)
        self.honesty_slider.setValue(self.personality.honesty)
        self.honesty_slider.valueChanged.connect(self.on_personality_change)
        honesty_layout.addWidget(self.honesty_slider)
        self.honesty_label = QLabel(f"{self.personality.honesty}%")
        honesty_layout.addWidget(self.honesty_label)
        personality_layout.addLayout(honesty_layout)
        
        # Personality summary
        self.personality_summary = QLabel(self.personality.get_personality_summary())
        self.personality_summary.setWordWrap(True)
        personality_layout.addWidget(self.personality_summary)
        
        personality_group.setLayout(personality_layout)
        layout.addWidget(personality_group)
        
        # Conversation group
        conversation_group = QGroupBox("Conversation")
        conversation_layout = QVBoxLayout()
        
        # Save history toggle
        self.save_history_checkbox = QCheckBox("Save Conversation History")
        self.save_history_checkbox.setChecked(self.conversation_manager.save_enabled)
        self.save_history_checkbox.stateChanged.connect(self.on_save_history_toggle)
        conversation_layout.addWidget(self.save_history_checkbox)
        
        # Clear history button
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        conversation_layout.addWidget(clear_button)
        
        conversation_group.setLayout(conversation_layout)
        layout.addWidget(conversation_group)
        
        # Spacer
        layout.addStretch()
    
    def on_personality_change(self):
        """Handle personality slider changes."""
        humor = self.humor_slider.value()
        honesty = self.honesty_slider.value()
        
        self.humor_label.setText(f"{humor}%")
        self.honesty_label.setText(f"{honesty}%")
        
        self.personality.set_humor(humor)
        self.personality.set_honesty(honesty)
        
        self.personality_summary.setText(self.personality.get_personality_summary())
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def on_save_history_toggle(self, state):
        """Handle save history checkbox toggle."""
        enabled = state == Qt.Checked
        self.conversation_manager.set_save_enabled(enabled)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_manager.clear_history()
    
    def get_humor(self) -> int:
        """Get current humor setting."""
        return self.humor_slider.value()
    
    def get_honesty(self) -> int:
        """Get current honesty setting."""
        return self.honesty_slider.value()





