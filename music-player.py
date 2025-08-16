"""
Desktop Music Player Application
Built with PyQt5 and pygame for audio playback
Features: Play/pause/skip, playlists, volume control, seek bar, persistent storage
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QSlider, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QSplitter,
    QMenuBar, QMenu, QAction, QInputDialog, QAbstractItemView
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


class AudioPlayer:
    """Handles audio playback using pygame mixer"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.duration = 0
        
    def load_song(self, file_path: str) -> bool:
        """Load a song file for playback"""
        try:
            pygame.mixer.music.load(file_path)
            self.current_song = file_path
            self.position = 0
            self.duration = self.get_song_duration(file_path)
            return True
        except pygame.error as e:
            print(f"Error loading song: {e}")
            return False
    
    def play(self):
        """Start or resume playback"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.play(start=self.position)
        self.is_playing = True
    
    def pause(self):
        """Pause playback"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.position = 0
    
    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)
    
    def get_song_duration(self, file_path: str) -> float:
        """Get song duration in seconds using mutagen"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is not None:
                return audio_file.info.length
        except Exception as e:
            print(f"Error getting duration: {e}")
        return 0.0
    
    def get_song_info(self, file_path: str) -> Dict[str, str]:
        """Extract song metadata"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is not None:
                title = audio_file.get('TIT2', [os.path.basename(file_path)])[0] if 'TIT2' in audio_file else os.path.basename(file_path)
                artist = audio_file.get('TPE1', ['Unknown Artist'])[0] if 'TPE1' in audio_file else 'Unknown Artist'
                return {'title': str(title), 'artist': str(artist)}
        except Exception as e:
            print(f"Error getting song info: {e}")
        
        return {'title': os.path.basename(file_path), 'artist': 'Unknown Artist'}
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy() and self.is_playing


class PlaylistManager:
    """Manages playlists and persistent storage"""
    
    def __init__(self, data_dir: str = "music_player_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.playlists_file = self.data_dir / "playlists.json"
        self.playlists = self.load_playlists()
    
    def load_playlists(self) -> Dict[str, List[str]]:
        """Load playlists from persistent storage"""
        try:
            if self.playlists_file.exists():
                with open(self.playlists_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading playlists: {e}")
        return {"Default": []}
    
    def save_playlists(self):
        """Save playlists to persistent storage"""
        try:
            with open(self.playlists_file, 'w') as f:
                json.dump(self.playlists, f, indent=2)
        except Exception as e:
            print(f"Error saving playlists: {e}")
    
    def create_playlist(self, name: str) -> bool:
        """Create a new playlist"""
        if name not in self.playlists:
            self.playlists[name] = []
            self.save_playlists()
            return True
        return False
    
    def delete_playlist(self, name: str) -> bool:
        """Delete a playlist"""
        if name in self.playlists and name != "Default":
            del self.playlists[name]
            self.save_playlists()
            return True
        return False
    
    def add_song_to_playlist(self, playlist_name: str, song_path: str):
        """Add a song to a playlist"""
        if playlist_name in self.playlists:
            if song_path not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(song_path)
                self.save_playlists()
    
    def remove_song_from_playlist(self, playlist_name: str, song_path: str):
        """Remove a song from a playlist"""
        if playlist_name in self.playlists:
            if song_path in self.playlists[playlist_name]:
                self.playlists[playlist_name].remove(song_path)
                self.save_playlists()
    
    def get_playlist_songs(self, playlist_name: str) -> List[str]:
        """Get all songs in a playlist"""
        return self.playlists.get(playlist_name, [])
    
    def get_playlist_names(self) -> List[str]:
        """Get all playlist names"""
        return list(self.playlists.keys())


class MusicPlayerWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.audio_player = AudioPlayer()
        self.playlist_manager = PlaylistManager()
        self.current_playlist = "Default"
        self.current_song_index = 0
        self.current_songs = []
        
        # Timer for updating UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.start(100)  # Update every 100ms
        
        self.init_ui()
        self.load_current_playlist()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Desktop Music Player")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Playlists
        self.create_playlist_panel(splitter)
        
        # Right panel - Player controls and current song info
        self.create_player_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply styling
        self.apply_styles()
    
    def create_playlist_panel(self, parent):
        """Create the playlist management panel"""
        playlist_widget = QWidget()
        playlist_layout = QVBoxLayout(playlist_widget)
        
        # Playlist selection and management
        playlist_group = QGroupBox("Playlists")
        playlist_group_layout = QVBoxLayout(playlist_group)
        
        # Playlist buttons
        playlist_buttons_layout = QHBoxLayout()
        self.new_playlist_btn = QPushButton("New Playlist")
        self.delete_playlist_btn = QPushButton("Delete Playlist")
        self.new_playlist_btn.clicked.connect(self.create_new_playlist)
        self.delete_playlist_btn.clicked.connect(self.delete_current_playlist)
        
        playlist_buttons_layout.addWidget(self.new_playlist_btn)
        playlist_buttons_layout.addWidget(self.delete_playlist_btn)
        playlist_group_layout.addLayout(playlist_buttons_layout)
        
        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self.on_playlist_selected)
        playlist_group_layout.addWidget(self.playlist_list)
        
        playlist_layout.addWidget(playlist_group)
        
        # Songs in current playlist
        songs_group = QGroupBox("Songs")
        songs_group_layout = QVBoxLayout(songs_group)
        
        # Song management buttons
        song_buttons_layout = QHBoxLayout()
        self.add_songs_btn = QPushButton("Add Songs")
        self.remove_song_btn = QPushButton("Remove Song")
        self.add_songs_btn.clicked.connect(self.add_songs_to_playlist)
        self.remove_song_btn.clicked.connect(self.remove_song_from_playlist)
        
        song_buttons_layout.addWidget(self.add_songs_btn)
        song_buttons_layout.addWidget(self.remove_song_btn)
        songs_group_layout.addLayout(song_buttons_layout)
        
        # Songs list
        self.songs_list = QListWidget()
        self.songs_list.itemDoubleClicked.connect(self.on_song_double_clicked)
        self.songs_list.setSelectionMode(QAbstractItemView.SingleSelection)
        songs_group_layout.addWidget(self.songs_list)
        
        playlist_layout.addWidget(songs_group)
        parent.addWidget(playlist_widget)
    
    def create_player_panel(self, parent):
        """Create the main player control panel"""
        player_widget = QWidget()
        player_layout = QVBoxLayout(player_widget)
        
        # Current song info
        info_group = QGroupBox("Now Playing")
        info_layout = QVBoxLayout(info_group)
        
        self.song_title_label = QLabel("No song selected")
        self.song_artist_label = QLabel("")
        self.song_title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.song_artist_label.setFont(QFont("Arial", 10))
        
        info_layout.addWidget(self.song_title_label)
        info_layout.addWidget(self.song_artist_label)
        player_layout.addWidget(info_group)
        
        # Progress bar and time labels
        progress_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.sliderPressed.connect(self.on_seek_start)
        self.progress_bar.sliderReleased.connect(self.on_seek_end)
        self.total_time_label = QLabel("0:00")
        
        progress_layout.addWidget(self.current_time_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.total_time_label)
        player_layout.addLayout(progress_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮ Previous")
        self.play_pause_btn = QPushButton("▶ Play")
        self.stop_btn = QPushButton("⏹ Stop")
        self.next_btn = QPushButton("⏭ Next")
        
        self.prev_btn.clicked.connect(self.previous_song)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.stop_btn.clicked.connect(self.stop_playback)
        self.next_btn.clicked.connect(self.next_song)
        
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.next_btn)
        player_layout.addLayout(controls_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_label = QLabel("70%")
        
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        player_layout.addLayout(volume_layout)
        
        # Add stretch to push everything to top
        player_layout.addStretch()
        
        parent.addWidget(player_widget)
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        add_songs_action = QAction('Add Songs to Playlist', self)
        add_songs_action.triggered.connect(self.add_songs_to_playlist)
        file_menu.addAction(add_songs_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Playlist menu
        playlist_menu = menubar.addMenu('Playlist')
        
        new_playlist_action = QAction('New Playlist', self)
        new_playlist_action.triggered.connect(self.create_new_playlist)
        playlist_menu.addAction(new_playlist_action)
    
    def apply_styles(self):
        """Apply custom styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #3a3a3a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 4px;
            }
        """)
    
    def load_current_playlist(self):
        """Load and display the current playlist"""
        # Update playlist list
        self.playlist_list.clear()
        for playlist_name in self.playlist_manager.get_playlist_names():
            item = QListWidgetItem(playlist_name)
            self.playlist_list.addItem(item)
            if playlist_name == self.current_playlist:
                item.setSelected(True)
        
        # Update songs list
        self.update_songs_list()
    
    def update_songs_list(self):
        """Update the songs list for the current playlist"""
        self.songs_list.clear()
        self.current_songs = self.playlist_manager.get_playlist_songs(self.current_playlist)
        
        for song_path in self.current_songs:
            if os.path.exists(song_path):
                song_info = self.audio_player.get_song_info(song_path)
                display_text = f"{song_info['title']} - {song_info['artist']}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, song_path)
                self.songs_list.addItem(item)
    
    def on_playlist_selected(self, item):
        """Handle playlist selection"""
        self.current_playlist = item.text()
        self.update_songs_list()
    
    def on_song_double_clicked(self, item):
        """Handle song double-click to play"""
        song_path = item.data(Qt.UserRole)
        self.current_song_index = self.current_songs.index(song_path)
        self.play_current_song()
    
    def create_new_playlist(self):
        """Create a new playlist"""
        name, ok = QInputDialog.getText(self, 'New Playlist', 'Enter playlist name:')
        if ok and name:
            if self.playlist_manager.create_playlist(name):
                self.load_current_playlist()
            else:
                QMessageBox.warning(self, 'Error', 'Playlist already exists!')
    
    def delete_current_playlist(self):
        """Delete the currently selected playlist"""
        if self.current_playlist == "Default":
            QMessageBox.warning(self, 'Error', 'Cannot delete the Default playlist!')
            return
        
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                   f'Are you sure you want to delete "{self.current_playlist}"?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.playlist_manager.delete_playlist(self.current_playlist)
            self.current_playlist = "Default"
            self.load_current_playlist()
    
    def add_songs_to_playlist(self):
        """Add songs to the current playlist"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select Audio Files', '', 
            'Audio Files (*.mp3 *.wav *.ogg *.m4a);;All Files (*)'
        )
        
        for file_path in file_paths:
            self.playlist_manager.add_song_to_playlist(self.current_playlist, file_path)
        
        self.update_songs_list()
    
    def remove_song_from_playlist(self):
        """Remove selected song from playlist"""
        current_item = self.songs_list.currentItem()
        if current_item:
            song_path = current_item.data(Qt.UserRole)
            self.playlist_manager.remove_song_from_playlist(self.current_playlist, song_path)
            self.update_songs_list()
    
    def play_current_song(self):
        """Play the currently selected song"""
        if self.current_songs and 0 <= self.current_song_index < len(self.current_songs):
            song_path = self.current_songs[self.current_song_index]
            
            if os.path.exists(song_path):
                if self.audio_player.load_song(song_path):
                    self.audio_player.play()
                    self.update_song_info(song_path)
                    self.play_pause_btn.setText("⏸ Pause")
                    
                    # Highlight current song in list
                    for i in range(self.songs_list.count()):
                        item = self.songs_list.item(i)
                        if item.data(Qt.UserRole) == song_path:
                            self.songs_list.setCurrentItem(item)
                            break
                else:
                    QMessageBox.warning(self, 'Error', 'Could not load the selected song!')
            else:
                QMessageBox.warning(self, 'Error', 'Song file not found!')
    
    def update_song_info(self, song_path):
        """Update the current song information display"""
        song_info = self.audio_player.get_song_info(song_path)
        self.song_title_label.setText(song_info['title'])
        self.song_artist_label.setText(f"by {song_info['artist']}")
        
        # Update total time
        duration = self.audio_player.duration
        self.total_time_label.setText(self.format_time(duration))
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.audio_player.is_playing:
            self.audio_player.pause()
            self.play_pause_btn.setText("▶ Play")
        else:
            if self.audio_player.current_song:
                self.audio_player.play()
                self.play_pause_btn.setText("⏸ Pause")
            else:
                # No song loaded, play first song in playlist
                if self.current_songs:
                    self.current_song_index = 0
                    self.play_current_song()
    
    def stop_playback(self):
        """Stop playback"""
        self.audio_player.stop()
        self.play_pause_btn.setText("▶ Play")
        self.current_time_label.setText("0:00")
        self.progress_bar.setValue(0)
    
    def previous_song(self):
        """Play previous song in playlist"""
        if self.current_songs:
            self.current_song_index = (self.current_song_index - 1) % len(self.current_songs)
            self.play_current_song()
    
    def next_song(self):
        """Play next song in playlist"""
        if self.current_songs:
            self.current_song_index = (self.current_song_index + 1) % len(self.current_songs)
            self.play_current_song()
    
    def on_volume_changed(self, value):
        """Handle volume slider changes"""
        volume = value / 100.0
        self.audio_player.set_volume(volume)
        self.volume_label.setText(f"{value}%")
    
    def on_seek_start(self):
        """Handle seek bar press"""
        self.seeking = True
    
    def on_seek_end(self):
        """Handle seek bar release"""
        if hasattr(self, 'seeking') and self.seeking:
            # Note: pygame doesn't support seeking, so this is a placeholder
            # In a full implementation, you'd need a different audio library
            self.seeking = False
    
    def update_progress(self):
        """Update progress bar and time display"""
        if self.audio_player.is_music_playing():
            # Note: pygame doesn't provide position info, so this is estimated
            # In a full implementation, you'd use a library that supports position tracking
            pass
        elif self.audio_player.is_playing and not self.audio_player.is_music_playing():
            # Song finished, play next
            self.next_song()
    
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def closeEvent(self, event):
        """Handle application close"""
        self.audio_player.stop()
        pygame.mixer.quit()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Music Player")
    
    # Create and show the main window
    window = MusicPlayerWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
