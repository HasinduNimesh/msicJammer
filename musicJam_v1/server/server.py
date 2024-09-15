from flask import Flask
from flask_socketio import SocketIO, emit
from time import time

app = Flask(__name__)
socketio = SocketIO(app)

is_song_playing = False

@app.route('/')
def index():
    return "Music Jam Server is running!"

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('sync_time', {'server_time': time()}, broadcast=True)

@socketio.on('play_song')
def handle_play_song(data):
    global is_song_playing
    if not is_song_playing:
        print(f"Playing song: {data['song_name']}")
        emit('play_song', data, broadcast=True)  # Broadcast play event to all clients
        is_song_playing = True
    else:
        print(f"Song already playing: {data['song_name']}")

@socketio.on('pause_song')
def handle_pause_song():
    emit('pause_song', broadcast=True)

@socketio.on('resume_song')
def handle_resume_song():
    emit('resume_song', broadcast=True)

@socketio.on('stop_song')
def handle_stop_song():
    global is_song_playing
    print("Stopping song")
    emit('stop_song', broadcast=True)
    is_song_playing = False  # Reset the playing flag after stopping

@socketio.on('song_finished')
def handle_song_finished():
    global is_song_playing
    print("Song finished playing")
    is_song_playing = False  # Reset when the song finishes

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
