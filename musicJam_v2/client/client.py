# client.py
import socketio
import pygame
import threading

# Create a Socket.IO client
sio = socketio.Client()

# Initialize pygame mixer
pygame.mixer.init()

# Variable to track the current session code
current_session_code = None

def play_song(song_path):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()  # Ensure the previous song is stopped

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        print(f"Playing song: {song_path}")

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Notify the server that the song finished playing
        sio.emit('song_finished', {'session_code': current_session_code})
        print("Song finished playing.")
        
    except pygame.error as e:
        print(f"Error loading or playing song: {e}")

def pause_song():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        print("Song paused")
    else:
        print("No song is playing to pause")

def resume_song():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.unpause()
        print("Song resumed")
    else:
        print("No song to resume")

def stop_song():
    pygame.mixer.music.stop()  # Stop the music
    pygame.mixer.quit()  # Reset the mixer to clear any internal state
    pygame.mixer.init()  # Re-initialize the mixer
    print("Song stopped and mixer reset")
    sio.emit('stop_song', {'session_code': current_session_code})

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('play_song')
def on_play_song(data):
    global current_session_code
    song_path = data['song_path']
    print(f"Received play command for song: {song_path}")
    threading.Thread(target=play_song, args=(song_path,), daemon=True).start()

@sio.on('pause_song')
def on_pause_song(data):
    print("Received pause command")
    pause_song()

@sio.on('resume_song')
def on_resume_song(data):
    print("Received resume command")
    resume_song()

@sio.on('stop_song')
def on_stop_song(data):
    print("Received stop command")
    stop_song()

# Function to connect to the server
def run_socketio():
    try:
        sio.connect('http://localhost:5000')
    except Exception as e:
        print(f"Unable to connect to server: {e}")

# Start the Socket.IO client thread
socket_thread = threading.Thread(target=run_socketio, daemon=True)
socket_thread.start()

# Keep the main thread alive
sio.wait()
