"""Geometric block animation widget synchronized with speech."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
import math
import time


class GeometricAnimationWidget(QWidget):
    """3D-style geometric block animation inspired by TARS."""
    
    def __init__(self):
        super().__init__()
        self.animation_active = False
        self.rotation_angle = 0.0
        self.block_positions = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)  # ~60 FPS
        
        # Initialize block positions (3x3 grid of blocks)
        self.init_blocks()
    
    def init_blocks(self):
        """Initialize block positions."""
        self.block_positions = []
        grid_size = 3
        spacing = 0.3
        
        for i in range(grid_size):
            for j in range(grid_size):
                self.block_positions.append({
                    'x': (i - 1) * spacing,
                    'y': (j - 1) * spacing,
                    'z': 0.0,
                    'rotation': 0.0
                })
    
    def start_animation(self):
        """Start the animation."""
        self.animation_active = True
        if not self.animation_timer.isActive():
            self.animation_timer.start()
    
    def stop_animation(self):
        """Stop the animation."""
        self.animation_active = False
    
    def update_animation(self):
        """Update animation frame."""
        if self.animation_active:
            self.rotation_angle += 0.05
            
            # Update block positions and rotations
            for i, block in enumerate(self.block_positions):
                # Rotate blocks
                block['rotation'] = self.rotation_angle + i * 0.3
                
                # Add some vertical movement
                block['z'] = math.sin(self.rotation_angle + i) * 0.1
            
            self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Paint the animation."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dark background
        painter.fillRect(self.rect(), QColor(20, 20, 30))
        
        if not self.animation_active:
            # Static state - show idle blocks
            self.draw_blocks(painter, 0.0)
        else:
            # Animated state
            self.draw_blocks(painter, self.rotation_angle)
    
    def draw_blocks(self, painter, rotation):
        """Draw geometric blocks."""
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        scale = min(width, height) * 0.3
        
        # Draw each block
        for block in self.block_positions:
            # Calculate 3D position
            x = block['x'] * scale
            y = block['y'] * scale
            z = block['z'] * scale
            
            # Apply rotation
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            
            # Rotate around center
            rotated_x = x * cos_r - y * sin_r
            rotated_y = x * sin_r + y * cos_r
            
            # Project to 2D (simple isometric)
            screen_x = center_x + rotated_x + z * 0.5
            screen_y = center_y + rotated_y - z * 0.5
            
            # Block size
            block_size = scale * 0.15
            
            # Draw block (simple rectangle for now)
            color_intensity = int(150 + z * 50)
            color = QColor(color_intensity, color_intensity, 255)
            
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            
            # Draw block as rectangle
            rect_size = block_size * (1 + z * 0.3)
            painter.drawRect(
                int(screen_x - rect_size / 2),
                int(screen_y - rect_size / 2),
                int(rect_size),
                int(rect_size)
            )





