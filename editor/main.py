#!/usr/bin/env python3

"""
OpenFF Game Editor - Main Entry Point

This script launches the OpenFF Game Editor application.
"""

import sys
import os
import time
import random

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QProgressBar
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Try different import approaches
try:
    # Try direct import
    from main_window import MainWindow
    from utils.theme import apply_theme
except ImportError:
    # Try package import
    from editor.main_window import MainWindow
    from editor.utils.theme import apply_theme

class EnhancedSplashScreen(QSplashScreen):
    """Enhanced splash screen with progress bar and custom styling."""
    
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # Create progress bar
        self.progress_bar = QProgressBar(self)
        pixmap_size = pixmap.size()
        bar_width = int(pixmap_size.width() * 0.7)
        
        # Position the progress bar at the bottom center
        self.progress_bar.setGeometry(
            (pixmap_size.width() - bar_width) // 2,
            pixmap_size.height() - 50,
            bar_width,
            15
        )
        
        # Style the progress bar
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #5A5A5A;
                border-radius: 5px;
                background: rgba(0, 0, 0, 120);
                padding: 0px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A88FF, stop:1 #8AAFFF);
                border-radius: 3px;
            }
        """)
        
        # Set initial progress
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Initialize loading messages
        self.loading_messages = [
            "Loading OpenFF Game Editor...",
            "Initializing rendering engine...",
            "Loading resource packs...",
            "Preparing workspace...",
            "Loading game assets...",
            "Configuring editor tools...",
            "Getting things ready...",
            "Almost there..."
        ]
        self.current_message = 0
        
        # Setup media player for background music
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)  # Set volume to 50%
        
    def drawContents(self, painter):
        """Override to customize the look of the splash screen."""
        # Create a semi-transparent overlay for text background
        painter.setOpacity(0.7)
        painter.fillRect(0, self.height() - 90, self.width(), 90, QColor(0, 0, 0))
        
        # Reset opacity for text
        painter.setOpacity(1.0)
        
        # Set fancy font for message
        font = QFont("Arial", 11, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Draw the message with a subtle shadow effect
        message = self.loading_messages[self.current_message % len(self.loading_messages)]
        
        # Draw text shadow
        painter.setPen(QColor(0, 0, 0, 180))
        painter.drawText(self.rect().adjusted(2, 2, 0, -20), 
                       Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                       message)
        
        # Draw main text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(self.rect().adjusted(0, 0, 0, -20), 
                       Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                       message)
        
        # Draw version and copyright info
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 0, -10, -5),
                       Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                       "OpenFF Game Editor v1.0.0")
                       
    def play_music(self, music_path):
        """Play background music."""
        if os.path.exists(music_path):
            print(f"Playing background music: {music_path}")
            self.player.setSource(QUrl.fromLocalFile(music_path))
            self.player.setLoops(QMediaPlayer.Loops.Infinite)  # Loop the music
            self.player.play()
        else:
            print(f"Background music file not found: {music_path}")
    
    def stop_music(self):
        """Stop the background music."""
        print("Stopping background music")
        self.player.stop()

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    apply_theme(app)
    
    # Show splash screen with background image
    splash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'bg.png')
    
    # If splash image doesn't exist, create a blank pixmap
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        print(f"Using splash image: {splash_path}")
    else:
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.GlobalColor.white)
        print("Using default blank splash image")
    
    # Create enhanced splash screen
    splash = EnhancedSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents()
    
    # Play background music
    bgm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'mp3', 'bgm', 'SEMO-00001_01_loop.mp3')
    splash.play_music(bgm_path)
    
    # Create a timer for progress updates
    progress = 0
    loading_finished = False
    
    # Create window at the beginning to avoid issues
    window = MainWindow()
    window_data_loaded = False
    
    def update_progress():
        nonlocal progress, window_data_loaded, loading_finished
        
        # If loading is already finished, don't continue
        if loading_finished:
            return
            
        # Increment progress
        progress += random.randint(1, 5)
        if progress > 100:
            progress = 100
            
        # Update progress bar
        splash.progress_bar.setValue(progress)
        
        # Change message occasionally
        if progress % 15 == 0:
            splash.current_message = (splash.current_message + 1) % len(splash.loading_messages)
            splash.repaint()
        
        # When progress hits certain marks, do actual loading steps
        if progress >= 60 and not window_data_loaded:
            # Load game data
            try:
                print("Loading game data...")
                window.load_game_data()
                window_data_loaded = True
                print("Game data loaded successfully")
            except Exception as e:
                print(f"Error loading game data: {str(e)}")
                window_data_loaded = True  # Mark as loaded even if error to avoid trying again
        
        # When progress reaches 100%        
        if progress >= 100 and not loading_finished:
            print("Loading complete, preparing to show main window...")
            loading_finished = True
            timer.stop()
            
            # Force process events before transitioning
            app.processEvents()
            
            # Use direct call instead of a timer for transition
            finish_loading(window, splash)
    
    def finish_loading(window, splash):
        print("Finishing loading process...")
        
        # Stop the music when transitioning to main window
        splash.stop_music()
        
        # Show the main window
        window.show()
        print("Main window shown")
        
        # Finish the splash screen
        splash.finish(window)
        print("Splash screen finished")
        
        # Force processing events again to ensure UI updates
        app.processEvents()
    
    # Set up timer for progress updates
    timer = QTimer()
    timer.timeout.connect(update_progress)
    timer.start(100)  # Update every 100ms
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 