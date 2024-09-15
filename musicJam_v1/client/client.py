import socketio
from player import play_song, pause_song, resume_song
import threading

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server!")

@sio.on('sync_time')
def sync_time(data):
    print(f"Server time received: {data['server_time']}")

is_playing = False  # Variable to track whether a song is currently playing

@sio.on('play_song')
def on_play_song(data):
    global is_playing
    song_name = data['song_name']
    if not is_playing:  # Only play if no song is currently playing
        print(f"Playing song: {song_name}")
        play_thread = threading.Thread(target=play_song, args=(song_name,))
        play_thread.start()  # Play the song in a separate thread
        is_playing = True
    else:
        print(f"Song already playing: {song_name}")

@sio.on('pause_song')
def on_pause_song():
    print("Pausing song")
    pause_song()

@sio.on('resume_song')
def on_resume_song():
    print("Resuming song")
    resume_song()

def run_socketio():
    sio.connect('http://localhost:5000')
    sio.wait()

# Start Socket.IO in a new thread
socket_thread = threading.Thread(target=run_socketio)
socket_thread.daemon = True
socket_thread.start()
