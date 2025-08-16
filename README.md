# Desktop Music Player

A fully functional desktop music player application built with Python, PyQt5, and pygame.

## Features

- **Playback Controls**: Play, pause, resume, skip (next/previous), and stop music
- **Playlist Management**: Create, manage, and save multiple playlists
- **Song Information**: Display song title, artist, and duration
- **Volume Control**: Adjustable volume slider
- **Seek Bar**: Navigate within tracks (visual indicator)
- **Modern GUI**: User-friendly and visually appealing interface
- **Multiple Formats**: Support for MP3, WAV, OGG, and M4A files
- **Persistent Storage**: Playlists are saved and restored between sessions
- **Clean Code**: Well-structured, modular code with detailed comments

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Install Dependencies

1. Clone or download this project
2. Navigate to the project directory
3. Install the required packages:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Alternative Installation (if requirements.txt doesn't work)

Install packages individually:

\`\`\`bash
pip install PyQt5==5.15.9
pip install pygame==2.5.2
pip install mutagen==1.47.0
\`\`\`

## Running the Application

1. Navigate to the project directory
2. Run the music player:

\`\`\`bash
python scripts/music_player.py
\`\`\`

## Usage

### Getting Started

1. **Create a Playlist**: Click "New Playlist" to create your first playlist
2. **Add Songs**: Click "Add Songs" to browse and select audio files
3. **Play Music**: Double-click any song in the playlist to start playing
4. **Control Playback**: Use the play/pause, stop, previous, and next buttons

### Playlist Management

- **Create Playlist**: Click "New Playlist" and enter a name
- **Switch Playlists**: Click on any playlist name in the left panel
- **Delete Playlist**: Select a playlist and click "Delete Playlist" (cannot delete "Default")
- **Add Songs**: Select a playlist and click "Add Songs" to browse for audio files
- **Remove Songs**: Select a song and click "Remove Song"

### Playback Features

- **Play/Pause**: Click the play/pause button or double-click a song
- **Skip Tracks**: Use Previous/Next buttons to navigate through the playlist
- **Volume Control**: Adjust the volume slider (0-100%)
- **Song Information**: View current song title and artist in the "Now Playing" section

### Supported File Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)

## Technical Details

### Architecture

The application is built with a modular architecture:

- **AudioPlayer**: Handles audio playback using pygame mixer
- **PlaylistManager**: Manages playlist data and persistent storage
- **MusicPlayerWindow**: Main GUI application using PyQt5

### Data Storage

- Playlists are automatically saved to `music_player_data/playlists.json`
- The application creates this directory automatically on first run
- All playlist data persists between application sessions

### Limitations

- Seek functionality is visual only (pygame limitation)
- Position tracking is estimated (pygame doesn't provide exact position)
- For full seek support, consider using python-vlc or similar libraries

## Troubleshooting

### Common Issues

1. **"No module named 'PyQt5'"**
   - Install PyQt5: `pip install PyQt5`

2. **"pygame.error: No available audio device"**
   - Check your system audio settings
   - Restart the application

3. **Songs not playing**
   - Verify the audio file format is supported
   - Check file permissions
   - Ensure the file path is correct

4. **GUI not displaying correctly**
   - Update PyQt5: `pip install --upgrade PyQt5`
   - Check your display settings

### Performance Tips

- Keep playlists under 1000 songs for optimal performance
- Use compressed audio formats (MP3) for better loading times
- Close other audio applications to avoid conflicts

## Future Enhancements

Potential improvements for future versions:

- Full seek functionality with python-vlc
- Equalizer controls
- Shuffle and repeat modes
- Album artwork display
- Keyboard shortcuts
- Import/export playlists
- Online streaming support

## License

This project is open source and available under the MIT License.
\`\`\`

```python file="scripts/install_dependencies.py"
"""
Dependency installer script for the Desktop Music Player
Automatically installs required packages
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main installation function"""
    print("Desktop Music Player - Dependency Installer")
    print("=" * 50)
    
    # Required packages
    packages = [
        ("PyQt5", "PyQt5==5.15.9"),
        ("pygame", "pygame==2.5.2"),
        ("mutagen", "mutagen==1.47.0")
    ]
    
    all_installed = True
    
    for package_name, package_spec in packages:
        print(f"\nChecking {package_name}...")
        
        if check_package(package_name):
            print(f"✓ {package_name} is already installed")
        else:
            print(f"Installing {package_name}...")
            if not install_package(package_spec):
                all_installed = False
    
    print("\n" + "=" * 50)
    
    if all_installed:
        print("✓ All dependencies installed successfully!")
        print("\nYou can now run the music player with:")
        print("python scripts/music_player.py")
    else:
        print("✗ Some dependencies failed to install.")
        print("Please install them manually using:")
        print("pip install PyQt5 pygame mutagen")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
