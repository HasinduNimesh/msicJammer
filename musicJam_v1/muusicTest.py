import pygame

pygame.mixer.init()
pygame.mixer.music.load('C:/Users/ASUS/Music/Downloads/Kailashini.mp3')
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play()

# Keep the script running while the song is playing
print("Playing music. Press Ctrl+C to stop.")
try:
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
except KeyboardInterrupt:
    pygame.mixer.music.stop()
    print("Music stopped.")
