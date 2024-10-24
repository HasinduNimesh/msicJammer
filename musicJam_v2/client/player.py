import pygame
import socketio

sio = socketio.Client()

def init_audio():
    try:
        pygame.mixer.init()
        print("Pygame audio initialized successfully")
    except pygame.error as e:
        print(f"Error initializing Pygame audio: {e}")

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
        sio.emit('song_finished')
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
    sio.emit('stop_song')  # Notify the server that the song has stopped

# Initialize audio when the module is loaded
init_audio()
