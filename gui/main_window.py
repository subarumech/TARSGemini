"""Main PyQt5 window for TARS AI Assistant."""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                             QLabel, QSlider, QCheckBox, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from core.gemini_client import GeminiClient
from core.text_to_speech import TextToSpeech
from core.conversation_manager import ConversationManager
from core.streaming_pipeline import StreamingPipeline
from core.response_cache import ResponseCache
from personality.tars_personality import TARSPersonality
from config.settings import DEFAULT_HUMOR, DEFAULT_HONESTY, SAVE_HISTORY_DEFAULT
from gui.geometric_animation import GeometricAnimationWidget
from gui.controls_panel import ControlsPanel
import threading


class ResponseWorker(QThread):
    """Worker thread for processing responses."""
    
    response_chunk = pyqtSignal(str)
    response_complete = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, pipeline, query):
        super().__init__()
        self.pipeline = pipeline
        self.query = query
    
    def run(self):
        try:
            for chunk in self.pipeline.process_query(
                self.query,
                on_sentence=lambda s: self.response_chunk.emit(s),
                on_complete=lambda: self.response_complete.emit()
            ):
                self.response_chunk.emit(chunk)
        except Exception as e:
            self.error.emit(str(e))


class TARSMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.personality = TARSPersonality(DEFAULT_HUMOR, DEFAULT_HONESTY)
        self.gemini_client = GeminiClient(
            system_instruction=self.personality.get_system_instruction()
        )
        self.tts = TextToSpeech()
        self.cache = ResponseCache()
        self.conversation_manager = ConversationManager(SAVE_HISTORY_DEFAULT)
        
        # Set conversation history in Gemini client
        self.gemini_client.set_conversation_history(
            self.conversation_manager.get_history_for_api()
        )
        
        # Initialize pipeline
        self.pipeline = StreamingPipeline(
            self.gemini_client,
            self.tts,
            self.personality,
            self.cache
        )
        
        # Worker thread
        self.response_worker = None
        
        # UI setup
        self.init_ui()
        self.setup_dark_theme()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("TARS AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel: Conversation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Conversation display
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setFont(QFont("Consolas", 10))
        left_layout.addWidget(QLabel("Conversation:"))
        left_layout.addWidget(self.conversation_display)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message or use microphone...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedWidth(50)
        self.mic_button.clicked.connect(self.toggle_microphone)
        input_layout.addWidget(self.mic_button)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        left_layout.addLayout(input_layout)
        
        splitter.addWidget(left_panel)
        
        # Center panel: Animation
        self.animation_widget = GeometricAnimationWidget()
        splitter.addWidget(self.animation_widget)
        
        # Right panel: Controls
        self.controls_panel = ControlsPanel(
            self.personality,
            self.conversation_manager,
            self.on_personality_changed
        )
        splitter.addWidget(self.controls_panel)
        
        # Set splitter sizes
        splitter.setSizes([400, 400, 300])
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def setup_dark_theme(self):
        """Apply dark theme."""
        dark_palette = QPalette()
        
        # Window
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        
        # Base
        dark_palette.setColor(QPalette.Base, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        
        # Text
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.yellow)
        
        # Button
        dark_palette.setColor(QPalette.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        
        # Highlight
        dark_palette.setColor(QPalette.Highlight, QColor(0, 100, 150))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(dark_palette)
    
    def send_message(self):
        """Send user message."""
        query = self.input_field.text().strip()
        if not query:
            return
        
        # Clear input
        self.input_field.clear()
        
        # Display user message
        self.add_to_conversation("You", query)
        
        # Update status
        self.statusBar().showMessage("Processing...")
        
        # Start animation
        self.animation_widget.start_animation()
        
        # Process in worker thread
        self.response_worker = ResponseWorker(self.pipeline, query)
        self.response_worker.response_chunk.connect(self.on_response_chunk)
        self.response_worker.response_complete.connect(self.on_response_complete)
        self.response_worker.error.connect(self.on_error)
        self.response_worker.start()
    
    def on_response_chunk(self, chunk: str):
        """Handle response chunk."""
        # Update status with current chunk being processed
        self.statusBar().showMessage(f"TARS speaking: {chunk[:50]}...")
    
    def on_response_complete(self):
        """Handle response completion."""
        # Get full response from Gemini client history
        history = self.gemini_client.conversation_history
        if history:
            last_response = history[-1]
            if last_response.get('role') == 'model':
                response_text = last_response.get('parts', [''])[0]
                self.add_to_conversation("TARS", response_text)
                
                # Save to conversation manager if enabled
                if self.conversation_manager.save_enabled:
                    user_msg = history[-2].get('parts', [''])[0] if len(history) >= 2 else ""
                    self.conversation_manager.add_exchange(
                        user_msg,
                        response_text,
                        self.personality.humor,
                        self.personality.honesty
                    )
        
        self.statusBar().showMessage("Ready")
        self.animation_widget.stop_animation()
    
    def on_error(self, error_msg: str):
        """Handle error."""
        self.statusBar().showMessage(f"Error: {error_msg}")
        self.add_to_conversation("System", f"Error: {error_msg}")
        self.animation_widget.stop_animation()
    
    def add_to_conversation(self, speaker: str, message: str):
        """Add message to conversation display."""
        color = "#4CAF50" if speaker == "You" else "#2196F3" if speaker == "TARS" else "#FF9800"
        self.conversation_display.append(
            f'<p style="color: {color};"><b>{speaker}:</b> {message}</p>'
        )
    
    def toggle_microphone(self):
        """Toggle microphone recording."""
        # TODO: Implement microphone functionality
        self.statusBar().showMessage("Microphone feature coming soon...")
    
    def on_personality_changed(self):
        """Handle personality settings change."""
        humor = self.controls_panel.get_humor()
        honesty = self.controls_panel.get_honesty()
        self.personality.set_humor(humor)
        self.personality.set_honesty(honesty)
        
        # Update Gemini model with new system instruction
        self.gemini_client.update_system_instruction(
            self.personality.get_system_instruction()
        )
        
        # Update status
        self.statusBar().showMessage(f"Personality updated: {self.personality.get_personality_summary()}")
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.response_worker and self.response_worker.isRunning():
            self.response_worker.terminate()
            self.response_worker.wait()
        
        self.pipeline.stop()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = TARSMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

