from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Lock to prevent race conditions
session_lock = threading.Lock()

# Dictionary to keep track of sessions
sessions = {}

# Route for the home page
@app.route('/')
def home():
    return "Welcome to the Music Jam App!"

# Event to create a new session
@socketio.on('create_session')
def handle_create_session(data):
    session_code = data['session_code']
    
    with session_lock:
        # Ensure session_code is unique
        if session_code in sessions:
            emit('error', {'message': 'Session code already exists.'}, room=request.sid)
            return

        # Initialize the session with the host's SID and an empty song
        sessions[session_code] = {'host': request.sid, 'song': None, 'clients': []}
    
    # Add the host to the session room
    join_room(session_code)
    
    # Notify the client that the session has been created
    emit('session_created', {'session_code': session_code}, room=request.sid)
    print(f"Session {session_code} created by {request.sid}.")

# Event to join an existing session
@socketio.on('join_session')
def handle_join_session(data):
    session_code = data['session_code']
    
    with session_lock:
        if session_code in sessions:
            join_room(session_code)
            sessions[session_code]['clients'].append(request.sid)
            emit('session_joined', {'session_code': session_code}, room=request.sid)
        else:
            emit('error', {'message': 'Session not found'}, room=request.sid)

# Event to play a song for the entire session (restricted to host)
@socketio.on('play_song')
def handle_play_song(data):
    session_code = data['session_code']
    song_path = data['song_path']

    with session_lock:
        if session_code in sessions and request.sid == sessions[session_code]['host']:
            sessions[session_code]['song'] = song_path
            emit('play_song', {'song_path': song_path}, room=session_code)
        else:
            emit('error', {'message': 'Unauthorized or session not found'}, room=request.sid)

# Event to pause the song (restricted to host)
@socketio.on('pause_song')
def handle_pause_song(data):
    session_code = data['session_code']

    with session_lock:
        if session_code in sessions and request.sid == sessions[session_code]['host']:
            emit('pause_song', room=session_code)
        else:
            emit('error', {'message': 'Unauthorized or session not found'}, room=request.sid)

# Event to resume the song (restricted to host)
@socketio.on('resume_song')
def handle_resume_song(data):
    session_code = data['session_code']

    with session_lock:
        if session_code in sessions and request.sid == sessions[session_code]['host']:
            emit('resume_song', room=session_code)
        else:
            emit('error', {'message': 'Unauthorized or session not found'}, room=request.sid)

# Event to stop the song (restricted to host)
@socketio.on('stop_song')
def handle_stop_song(data):
    session_code = data['session_code']

    with session_lock:
        if session_code in sessions and request.sid == sessions[session_code]['host']:
            emit('stop_song', room=session_code)
        else:
            emit('error', {'message': 'Unauthorized or session not found'}, room=request.sid)

# Event when a client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    with session_lock:
        for session_code, session_data in sessions.items():
            if request.sid == session_data['host']:
                # If the host disconnects, close the session
                emit('error', {'message': 'Host disconnected. Session closed.'}, room=session_code)
                del sessions[session_code]
                break
            elif request.sid in session_data['clients']:
                # Remove the client from the session
                session_data['clients'].remove(request.sid)
                break

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
