import tkinter as tk
from tkinter import filedialog
import threading
import socketio
import pygame

# Initialize pygame in the main thread
pygame.mixer.init()

# Create a Socket.IO client
sio = socketio.Client()

# Define event handlers for Socket.IO
@sio.event
def connect():
    print("Connected to server")
    status_label.config(text="Connected to server", fg="green")

@sio.event
def disconnect():
    print("Disconnected from server")
    status_label.config(text="Disconnected from server", fg="red")

@sio.event
def sync_time(data):
    print(f"Server time: {data['server_time']}")

# Function to handle playing the song
def play_song(song_path):
    try:
        # Stop any currently playing song before playing a new one
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(volume_slider.get() / 100)  # Set volume from the slider
        pygame.mixer.music.play()
        print(f"Playing song: {song_path}")

        song_name = song_path.split("/")[-1]  # Get only the song name from the path
        current_song_label.config(text=f"Now Playing: {song_name}")

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Notify the server when the song finishes
        sio.emit('song_finished')
        print("Song finished playing.")
        current_song_label.config(text="")  # Reset song name when finished
        
    except pygame.error as e:
        print(f"Error loading or playing song: {e}")

def on_play_song(data):
    song_path = data['song_name']
    threading.Thread(target=play_song, args=(song_path,)).start()  # Run play_song in a separate thread

# Register play_song event handler with Socket.IO
sio.on('play_song', on_play_song)

def play_song_gui():
    # Open a file dialog to select a song
    song_path = filedialog.askopenfilename(
        title="Select a song",
        filetypes=[("MP3 Files", "*.mp3")]
    )
    
    if song_path:
        sio.emit('play_song', {'song_name': song_path})  # Send the selected song path to the server
        print(f"Play song: {song_path}")

def pause_song():
    sio.emit('pause_song')
    print("Pause song")
    pygame.mixer.music.pause()  # Pause the song locally
    current_song_label.config(text="Paused")

def resume_song():
    sio.emit('resume_song')
    print("Resume song")
    pygame.mixer.music.unpause()  # Resume the song locally
    current_song_label.config(text="Resumed")

def stop_song():
    pygame.mixer.music.stop()  # Stop the music
    pygame.mixer.quit()  # Reset the mixer to clear any internal state
    pygame.mixer.init()  # Re-initialize the mixer
    print("Song stopped and mixer reset")
    sio.emit('stop_song')  # Notify the server that the song has stopped
    current_song_label.config(text="")  # Clear the song name when stopped

# Run the Socket.IO client in a separate thread
def run_socketio():
    sio.connect('http://localhost:5000')
    sio.wait()

# Start the Socket.IO client thread
socket_thread = threading.Thread(target=run_socketio)
socket_thread.daemon = True
socket_thread.start()

# Function to update the volume based on the slider
def update_volume(value):
    volume = int(value) / 100  # Convert slider value to a float between 0.0 and 1.0
    pygame.mixer.music.set_volume(volume)  # Set volume in pygame
    print(f"Volume set to: {volume}")

# Create the main application window
root = tk.Tk()
root.title("Music Jam Client")
root.geometry("400x400")  # Set the window size
root.config(bg="#f0f0f0")  # Set background color

# Create GUI components with better design
status_label = tk.Label(root, text="Connecting to server...", font=('Helvetica', 14), fg="gray", bg="#f0f0f0")
status_label.pack(pady=10)

current_song_label = tk.Label(root, text="", font=('Helvetica', 12, 'bold'), fg="#333333", bg="#f0f0f0")
current_song_label.pack(pady=5)

# Create a frame to hold the buttons for better layout
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=20)

# Buttons with color and font customization
play_button = tk.Button(button_frame, text="Play Song", command=play_song_gui, font=('Helvetica', 12), bg="#4CAF50", fg="white", padx=20, pady=5)
play_button.grid(row=0, column=0, padx=10, pady=5)

pause_button = tk.Button(button_frame, text="Pause", command=pause_song, font=('Helvetica', 12), bg="#FF9800", fg="white", padx=20, pady=5)
pause_button.grid(row=0, column=1, padx=10, pady=5)

resume_button = tk.Button(button_frame, text="Resume", command=resume_song, font=('Helvetica', 12), bg="#2196F3", fg="white", padx=20, pady=5)
resume_button.grid(row=1, column=0, padx=10, pady=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_song, font=('Helvetica', 12), bg="#F44336", fg="white", padx=20, pady=5)
stop_button.grid(row=1, column=1, padx=10, pady=5)

# Add a volume slider
volume_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', label="Volume", command=update_volume, font=('Helvetica', 12), bg="#f0f0f0", fg="#333333")
volume_slider.set(50)  # Set default volume to 50%
volume_slider.pack(pady=20)

# Add padding to the bottom
root.pack_propagate(0)
root.mainloop()
