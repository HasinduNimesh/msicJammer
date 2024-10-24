import time
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import threading
import socketio
import pygame
import random
import string

# Initialize pygame mixer
pygame.mixer.init()

# Create a Socket.IO client
sio = socketio.Client()

# Variables to track session code and connection status
current_session_code = None
is_host = False
is_connected = False  # Track the connection status

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Music Jam Client")
root.geometry("400x500")
root.config(bg="#f0f0f0")

# Initialize global variables for UI elements
current_song_label = None
status_label = None

# Function to handle playing the song
def play_song(song_path):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(volume_slider.get() / 100)  # Set volume from the slider
        pygame.mixer.music.play()
        print(f"Pygame: Playing song: {song_path}")

        song_name = song_path.split("/")[-1]
        current_song_label.config(text=f"Now Playing: {song_name}")

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        sio.emit('song_finished', {'session_code': current_session_code})
        current_song_label.config(text="")  # Reset song name when finished
        
    except pygame.error as e:
        print(f"Error loading or playing song: {e}")
        messagebox.showerror("Playback Error", f"Error playing song: {e}")

def on_play_song(data):
    song_path = data.get('song_path', None)
    if song_path:
        print(f"Client received song to play: {song_path}")  # Debugging
        threading.Thread(target=play_song, args=(song_path,), daemon=True).start()
    else:
        print("No song path received!")

# Register play_song event handler with Socket.IO
sio.on('play_song', on_play_song)

# Event handlers for Socket.IO
@sio.event
def connect():
    global is_connected
    is_connected = True
    print("Connected to server")
    status_label.config(text="Connected to server", fg="green")

@sio.event
def disconnect():
    global is_connected
    is_connected = False
    print("Disconnected from server")
    status_label.config(text="Disconnected from server", fg="red")

@sio.on('session_created')
def handle_session_created(data):
    session_code = data['session_code']
    print(f"Session {session_code} created")
    messagebox.showinfo("Session Created", f"Your session code is: {session_code}")

@sio.on('session_joined')
def handle_session_joined(data):
    session_code = data['session_code']
    print(f"Joined session {session_code}")
    messagebox.showinfo("Session Joined", f"Successfully joined session: {session_code}")

@sio.on('error')
def handle_error(data):
    print(f"Error: {data['message']}")
    messagebox.showerror("Error", data['message'])

# Function to initialize and connect the Socket.IO client
def run_socketio():
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            sio.connect('https://b9cc-112-134-171-28.ngrok-free.app')
            break
        except Exception as e:
            print(f"Unable to connect to server (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")

# Start the Socket.IO client thread
socket_thread = threading.Thread(target=run_socketio, daemon=True)
socket_thread.start()

# Function to generate a random session code
def generate_session_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Function to create a new session
def create_session():
    global is_host, current_session_code
    if not is_connected:
        messagebox.showwarning("Not Connected", "Not connected to the server yet.")
        return

    is_host = True
    session_code = generate_session_code()  # Generate a random session code
    current_session_code = session_code
    sio.emit('create_session', {'session_code': session_code})
    show_session_controls()

# Function to join an existing session
def join_session():
    global current_session_code
    if not is_connected:
        messagebox.showwarning("Not Connected", "Not connected to the server yet.")
        return

    session_code = simpledialog.askstring("Join Session", "Enter the session code:")
    if session_code:
        current_session_code = session_code
        sio.emit('join_session', {'session_code': session_code})
        # Transition to the control window
        show_session_controls()

# Function to show playback controls
def show_session_controls():
    global current_song_label, volume_slider

    session_controls_window = tk.Toplevel(root)
    session_controls_window.title("Session Controls")
    session_controls_window.geometry("400x400")
    session_controls_window.config(bg="#f0f0f0")

    # Status label inside session controls
    status_label_session = tk.Label(session_controls_window, text="Now Playing:", font=('Helvetica', 12, 'bold'), fg="#333333", bg="#f0f0f0")
    status_label_session.pack(pady=5)

    # Playback control buttons
    play_button = tk.Button(session_controls_window, text="Play Song", command=play_song_gui, font=('Helvetica', 12), bg="#4CAF50", fg="white", width=15)
    play_button.pack(pady=5)

    pause_button = tk.Button(session_controls_window, text="Pause", command=pause_song, font=('Helvetica', 12), bg="#FF9800", fg="white", width=15)
    pause_button.pack(pady=5)

    resume_button = tk.Button(session_controls_window, text="Resume", command=resume_song, font=('Helvetica', 12), bg="#2196F3", fg="white", width=15)
    resume_button.pack(pady=5)

    stop_button = tk.Button(session_controls_window, text="Stop", command=stop_song, font=('Helvetica', 12), bg="#F44336", fg="white", width=15)
    stop_button.pack(pady=5)

    # Volume control slider
    volume_slider = tk.Scale(session_controls_window, from_=0, to=100, orient='horizontal', label="Volume", command=update_volume, font=('Helvetica', 12), bg="#f0f0f0", fg="#333333")
    volume_slider.set(50)
    volume_slider.pack(pady=10)

    # Assign the status label for updating playback status
    current_song_label = status_label_session

# Function to play song from GUI
def play_song_gui():
    song_path = filedialog.askopenfilename(title="Select a song", filetypes=[("MP3 Files", "*.mp3")])
    if song_path:
        sio.emit('play_song', {'session_code': current_session_code, 'song_path': song_path})
        print(f"Play song: {song_path}")

# Function to pause the song
def pause_song():
    sio.emit('pause_song', {'session_code': current_session_code})
    pygame.mixer.music.pause()
    current_song_label.config(text="Paused")

# Function to resume the song
def resume_song():
    sio.emit('resume_song', {'session_code': current_session_code})
    pygame.mixer.music.unpause()
    current_song_label.config(text="Resumed")

# Function to stop the song
def stop_song():
    sio.emit('stop_song', {'session_code': current_session_code})
    pygame.mixer.music.stop()
    current_song_label.config(text="Stopped")

# Function to update the volume
def update_volume(value):
    volume = int(value) / 100
    pygame.mixer.music.set_volume(volume)
    print(f"Volume set to: {volume}")

# Create initial UI components
welcome_label = tk.Label(root, text="Welcome to Music Jam!", font=('Helvetica', 16), fg="black", bg="#f0f0f0")
welcome_label.pack(pady=20)

create_session_button = tk.Button(root, text="Create New Session", command=create_session, font=('Helvetica', 12), bg="#4CAF50", fg="white", padx=20, pady=10, width=20)
create_session_button.pack(pady=10)

join_session_button = tk.Button(root, text="Join Session", command=join_session, font=('Helvetica', 12), bg="#2196F3", fg="white", padx=20, pady=10, width=20)
join_session_button.pack(pady=10)

# Status label to show connection status
status_label = tk.Label(root, text="Connecting to server...", font=('Helvetica', 10), fg="red", bg="#f0f0f0")
status_label.pack(pady=20)

# Start the Tkinter main loop
root.mainloop()
