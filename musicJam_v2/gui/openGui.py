import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, simpledialog, messagebox
import threading
import socketio
import pygame
import random
import string
from PIL import Image, ImageTk
import os
from pathlib import Path
import tkinter.font as tkFont

######variables#######
app_instance = None

####Functions of code #####
# Initialize pygame mixer
pygame.mixer.init()

# Create a Socket.IO client
sio = socketio.Client()

# Variables to track session code and connection status
current_session_code = None
is_host = False
is_connected = False  # Track the connection status

def play_song(app_instance, song_path):
    try:
        # Debugging: Check if instance is of type NewSessionGUI
        if not isinstance(app_instance, NewSessionGUI):
            print("Error: instance is not of type NewSessionGUI")
            return

        # Debugging: Check if current_song_label is initialized
        if app_instance.current_song_label is None:
            print("Error: current_song_label is not initialized")
            return

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(app_instance.volume_slider.get() / 100)  # Set volume from the slider
        pygame.mixer.music.play()
        print(f"Pygame: Playing song: {song_path}")

        song_name = song_path.split("/")[-1]
        app_instance.current_song_label.config(text=f"{song_name}")

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        sio.emit('song_finished', {'session_code': current_session_code})
        app_instance.current_song_label.config(text="")  # Reset song name when finished

    except pygame.error as e:
        print(f"Error loading or playing song: {e}")
        messagebox.showerror("Playback Error", f"Error playing song: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")


# Event handlers for Socket.IO
@sio.event
def connect():
    global is_connected, app_instance
    is_connected = True
    print("Connected to server")
    app_instance.status_label.config(text="Connected to server ●", fg="green")

@sio.event
def disconnect():
    global is_connected, app_instance
    is_connected = False
    print("Disconnected from server")
    app_instance.status_label.config(text="Disconnected from server ●", fg="red")

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
def create_session(root):
    global is_host, current_session_code, app_instance
    if not is_connected:
        messagebox.showwarning("Not Connected", "Not connected to the server yet.")
        return
    
    is_host = True
    session_code = generate_session_code()  # Generate a random session code
    current_session_code = session_code
    print(f"Generated session code: {session_code}")  # Debugging print
    sio.emit('create_session', {'session_code': session_code})
    
    # Create the new session window and update the session ID text
    new_session_gui = NewSessionGUI(root)
    app_instance = new_session_gui  # Set the app_instance to the new session GUI
    new_session_gui.canvas.itemconfig(new_session_gui.session_id_text, text=session_code)
    new_session_gui.canvas.update_idletasks()  # Ensure the canvas is updated
    print(f"Updated session ID text: {session_code}")  # Debugging print

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
        currentSession()

####music functiions #####
        
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
    app_instance.current_song_label.config(text="Paused")

# Function to resume the song
def resume_song():
    sio.emit('resume_song', {'session_code': current_session_code})
    pygame.mixer.music.unpause()
    app_instance.current_song_label.config(text="Resumed")

# Function to stop the song
def stop_song():
    sio.emit('stop_song', {'session_code': current_session_code})
    pygame.mixer.music.stop()
    app_instance.current_song_label.config(text="Stopped")

# Function to update the volume
def update_volume(value):
    volume = int(value) / 100
    pygame.mixer.music.set_volume(volume)
    print(f"Volume set to: {volume}")

class  NewSessionGUI:
    def __init__(self, root):
        self.root = root
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = os.path.join(self.OUTPUT_PATH, "assests", "createpageAssests")

        self.image_references = []  # List to store image references

        self.setup_window()
        self.register_custom_font()
        self.create_widgets()
        self.bind_window_events()

        self.session_id_text = None  # Add this line to store the reference
        self.current_song_label = None  # Add this line to store the reference


    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def setup_window(self):
        self.root.geometry("670x384")
        self.root.configure(bg="#000000")
        self.root.overrideredirect(True)  # Remove window decorations

        # Center the window on the screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def register_custom_font(self):
        font_path = os.path.join(self.ASSETS_PATH, "Anybody-Regular.ttf")
        
    def create_custom_font(self, size):
        return tk.font.Font(family="Anybody Regular", size=size)

    def close_window(self):
        self.root.destroy()

    def minimize_window(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def restore_window(self, event):
        if self.root.state() == 'normal':
            self.root.overrideredirect(True)

    def bind_window_events(self):
        # Bind window dragging functions or other events here
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_motion)

    def start_move(self, event):
        # Check if the event is from the slider
        if event.widget == self.volume_slider:
            return
        self.root.x = event.x
        self.root.y = event.y

    def stop_move(self, event):
        # Check if the event is from the slider
        if event.widget == self.volume_slider:
            return
        self.root.x = None
        self.root.y = None

    def on_motion(self, event):
        # Check if the event is from the slider
        if event.widget == self.volume_slider:
            return
        x = (event.x_root - self.root.x)
        y = (event.y_root - self.root.y)
        self.root.geometry(f"+{x}+{y}")

    def load_image(self, image_path, width):
        img = Image.open(image_path)
        img = img.convert("RGBA")  # Ensure image is in RGBA mode (with transparency)
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        img = img.resize((width, new_height), Image.LANCZOS)  # Resize the image
        return ImageTk.PhotoImage(img)

    def create_widgets(self):
        # Create a canvas to hold elements
        self.canvas = tk.Canvas(
            self.root,
            bg="#000000",
            height=384,
            width=670,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Create a blue rectangle on the left
        self.canvas.create_rectangle(
            0.0,
            0.0,
            379.0,
            384.0,
            fill="#007BFF",
            outline=""
        )

        # Create title text "Music Jammer" using the custom font
        self.canvas.create_text(
            18.0,
            5.0,  # Adjust this value to move the "Music" text higher
            anchor="nw",
            text="Music",
            fill="#FFFFFF",
            font=self.create_custom_font(48)  # Apply the custom font directly
        )

        self.canvas.create_text(
            18.0,
            53.0,  # Adjust this value to control the space between "Music" and "Jammer."
            anchor="nw",
            text="Jammer.",
            fill="#FFFFFF",
            font=self.create_custom_font(48)  # Apply the custom font directly
        )

        # Footer text
        self.canvas.create_text(
            458.0,
            365.0,
            anchor="nw",
            text="Developed by Hasindu Nimesh ©",
            fill="#FFFFFF",
            font=self.create_custom_font(10)  # You can use a smaller size for this
        )

        # Subtext "Join, Jam, and Enjoy Music Together!"
        self.canvas.create_text(
            18.0,
            121.0,  # Adjust this value to control the space between "Jammer." and the subtext
            anchor="nw",
            text="Join, Jam, and Enjoy Music Together!",
            fill="#FFFFFF",
            font=self.create_custom_font(14)  # Smaller font for subtext
        )

        # Place an image on the canvas
        image_1 = self.load_image(self.relative_to_assets("image_1.png"), 297)  # Provide the size (width) as the second argument
        self.image_references.append(image_1)  # Store reference to the image
        self.canvas.create_image(
            224.0,
            375.0,
            image=image_1
        )

        # Button 1 with PIL to handle transparency
        button_image_1 = self.load_image(self.relative_to_assets("button_1.png"), 192)
        self.image_references.append(button_image_1)  # Store reference to the image
        button_1 = tk.Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=play_song_gui,  # Directly call the play_song_gui function
            relief="flat",
            bg="#000000",  # Match background to avoid white border
            activebackground="#000000"
        )
        button_1.place(
            x=428.0,
            y=91.0,
            width=192.0,
            height=57.0
        )

        # Button 2 with PIL to handle transparency
        button_image_2 = self.load_image(self.relative_to_assets("button_2.png"), 192)
        self.image_references.append(button_image_2)  # Store reference to the image
        button_2 = tk.Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.go_to_previous_window,  # Directly assign the navigation function
            relief="flat",
            bg="#000000",  # Match background to avoid white border
            activebackground="#000000"
        )
        button_2.place(
            x=428.0,
            y=283.0,
            width=192.0,
            height=57.0
        )

        self.canvas.create_text(
            18.0,
            192.0,
            anchor="nw",
            text="Now Playing :",
            fill="#FFFFFF",
            font=self.create_custom_font(13)
        )

        # Create a label for the currently playing song
        self.current_song_label = tk.Label(
            self.root,
            text="No song playing",  # Default text
            bg="#000000",
            fg="#FFFFFF",
            font=self.create_custom_font(13)
        )
        self.current_song_label.place(x=120, y=192)  # Adjust the position as needed

        self.canvas.create_text(
            403.0,
            57.0,  # Adjust this value to move the "Session Id" text down
            anchor="nw",
            text="Session Id :",
            fill="#FFFFFF",
            font=self.create_custom_font(10)
        )

        # Create a text element for the session ID and store its reference
        self.session_id_text = self.canvas.create_text(
            500.0,  # Adjust the x-coordinate to position it correctly
            57.0,  # Same y-coordinate as the "Session Id :" text
            anchor="nw",
            text="",  # Initially empty
            fill="#FFFFFF",
            font=self.create_custom_font(10)
        )

        # Place the clipboard image on the canvas
        image_image_2 = self.load_image(self.relative_to_assets("image_2.png"), 18)  # Adjust the size as needed
        self.image_references.append(image_image_2)  # Store reference to the image
        clipboard_image = self.canvas.create_image(
            637.0,
            64.0,  # Adjust this value to move the clipboard image down
            image=image_image_2
        )

        # Bind the clipboard image to the copy function
        self.canvas.tag_bind(clipboard_image, "<Button-1>", lambda event: self.copy_to_clipboard(current_session_code))


        self.canvas.create_rectangle(
            409.0,
            186.0,
            645.0,
            189.0,
            fill="#FFFFFF",
            outline=""
        )

        image_image_3 = self.load_image(self.relative_to_assets("image_3.png"), 24)
        self.image_references.append(image_image_3)  # Store reference to the image
        self.canvas.create_image(
            479.0,
            218.0,
            image=image_image_3
        )

        image_image_4 = self.load_image(self.relative_to_assets("image_4.png"), 24)
        self.image_references.append(image_image_4)  # Store reference to the image
        self.canvas.create_image(
            573.0,
            218.0,
            image=image_image_4
        )

        image_image_5 = self.load_image(self.relative_to_assets("image_5.png"), 24)
        self.image_references.append(image_image_5)  # Store reference to the image
        self.canvas.create_image(
            526.0,
            219.0,
            image=image_image_5
        )

        # Create macOS-style close and minimize buttons
        def on_enter_close(event):
            close_button.config(text="x", fg="#FFFFFF", font=self.create_custom_font(14))

        def on_leave_close(event):
            close_button.config(text="●", fg="#FF5F56", font=self.create_custom_font(20))

        def on_enter_minimize(event):
            minimize_button.config(text="-", fg="#FFFFFF", font=self.create_custom_font(14))

        def on_leave_minimize(event):
            minimize_button.config(text="●", fg="#FFBD2E", font=self.create_custom_font(20))

        close_button = tk.Button(
            self.root,
            text="●",
            font=self.create_custom_font(20),  # Use custom font
            fg="#FF5F56",
            bg="#000000",
            borderwidth=0,
            command=self.close_window,
            activebackground="#000000"
        )
        close_button.place(x=640, y=10, width=24, height=24)  # Position at the top right
        close_button.bind("<Enter>", on_enter_close)
        close_button.bind("<Leave>", on_leave_close)

        minimize_button = tk.Button(
            self.root,
            text="●",
            font=self.create_custom_font(20),  # Use custom font
            fg="#FFBD2E",
            bg="#000000",
            borderwidth=0,
            command=self.minimize_window,
            activebackground="#000000"
        )
        minimize_button.place(x=610, y=10, width=24, height=24)  # Position at the top right
        minimize_button.bind("<Enter>", on_enter_minimize)
        minimize_button.bind("<Leave>", on_leave_minimize)

        ####music functiions #####
        
        # Function to pause the song
        def pause_song():
            sio.emit('pause_song', {'session_code': current_session_code})
            pygame.mixer.music.pause()
            self.current_song_label.config(text="Paused")

        # Function to resume the song
        def resume_song():
            sio.emit('resume_song', {'session_code': current_session_code})
            pygame.mixer.music.unpause()
            self.current_song_label.config(text="Resumed")

        # Function to stop the song
        def stop_song():
            sio.emit('stop_song', {'session_code': current_session_code})
            pygame.mixer.music.stop()
            self.current_song_label.config(text="Stopped")

        # Function to update the volume
        def update_volume(value):
            volume = float(value) / 100  # Convert to float instead of int
            pygame.mixer.music.set_volume(volume)
            print(f"Volume set to: {volume}")

        def copy_to_clipboard(session_code):
            self.root.clipboard_clear()
            self.root.clipboard_append(session_code)
            self.root.update()  # Now it stays on the clipboard after the window is closed
            messagebox.showinfo("Copied", f"Session code {session_code} copied to clipboard!")    

        # Create a volume slider using ttk
        self.volume_slider = ttk.Scale(
            self.root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            style="TScale",
            command=update_volume
        )
        self.volume_slider.set(50)  # Set default volume to 50%
        self.volume_slider.place(x=430, y=240, width=200)  # Adjust the position as needed

    # Create the main application window
    def go_to_previous_window(self):
        self.root.destroy()  # Close the current window
        openApp()  # Re-open the openApp window

    # Button click method
    def open_current_session(self):
        new_window = Toplevel(self.window)  # Open a new Toplevel window
        NewSessionGUI(new_window)  # Start the join session window

# Define a wrapper function to call play_song with the correct arguments
def on_play_song(data):
    song_path = data['song_path']
    play_song(app_instance, song_path)

# Register play_song event handler with Socket.IO
sio.on('play_song', on_play_song)

class openApp:
    global status_label
    def __init__(self):
        global app_instance
        app_instance = self
        # Paths to resources
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = os.path.join(self.OUTPUT_PATH, "assests", "openpageAssests")

        # Initialize the window
        self.window = tk.Tk()
        self.window.geometry("670x384")
        self.window.configure(bg="#000000")
        self.window.overrideredirect(True)  # Remove window decorations

        # Center the window on the screen
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # Register the custom font
        font_path = os.path.join(self.ASSETS_PATH, "Anybody-Regular.ttf")
        self.window.tk.call('font', 'create', 'AnybodyRegular', '-family', 'Anybody Regular', '-size', '10', '-weight', 'normal')
        self.window.tk.call('font', 'configure', 'AnybodyRegular', '-family', 'Anybody Regular', '-size', '10', '-weight', 'normal')

        # Bind the window dragging functions
        self.window.bind("<ButtonPress-1>", self.start_move)
        self.window.bind("<ButtonRelease-1>", self.stop_move)
        self.window.bind("<B1-Motion>", self.on_motion)
        self.window.bind("<Map>", self.restore_window)

        # Create a canvas to hold elements
        self.canvas = tk.Canvas(
            self.window,
            bg="#000000",
            height=384,
            width=670,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Create a blue rectangle on the left
        self.canvas.create_rectangle(
            0.0,
            0.0,
            379.0,
            384.0,
            fill="#007BFF",
            outline=""
        )

        # Create title text "Music Jammer" using the custom font
        self.canvas.create_text(
            18.0,
            5.0,  # Adjust this value to move the "Music" text higher
            anchor="nw",
            text="Music",
            fill="#FFFFFF",
            font=self.create_custom_font(48)  # Apply the custom font directly
        )

        self.canvas.create_text(
            18.0,
            53.0,  # Adjust this value to control the space between "Music" and "Jammer."
            anchor="nw",
            text="Jammer.",
            fill="#FFFFFF",
            font=self.create_custom_font(48)  # Apply the custom font directly
        )

        # Footer text
        self.canvas.create_text(
            458.0,
            365.0,
            anchor="nw",
            text="Developed by Hasindu Nimesh ©",
            fill="#FFFFFF",
            font=self.create_custom_font(10)  # You can use a smaller size for this
        )

        # Subtext "Join, Jam, and Enjoy Music Together!"
        self.canvas.create_text(
            18.0,
            130.0,  # Adjust this value to control the space between "Jammer." and the subtext
            anchor="nw",
            text="Join, Jam, and Enjoy Music Together!",
            fill="#FFFFFF",
            font=self.create_custom_font(14)  # Smaller font for subtext
        )

        # Place an image on the canvas
        image_1_path = self.relative_to_assets("image_1open.png")
        print(f"Loading image from: {image_1_path}")  # Debug print statement
        image_1 = self.load_image(image_1_path)
        self.canvas.create_image(
            224.0,
            375.0,
            image=image_1
        )

        # Button 1 with PIL to handle transparency
        button_image_1 = self.load_image(self.relative_to_assets("button_1open.png"))
        button_1 = tk.Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: create_session(self.window),  # Call create_session with the root window
            relief="flat",
            bg="#000000",  # Match background to avoid white border
            activebackground="#000000"
        )
        button_1.place(
            x=435.0,
            y=114.0,
            width=192.0,
            height=57.0
        )

        # Button 2 with PIL to handle transparency
        button_image_2 = self.load_image(self.relative_to_assets("button_2open.png"))
        button_2 = tk.Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: currentSession(self.window),  # Open the join session window
            relief="flat",
            bg="#000000",  # Match background to avoid white border
            activebackground="#000000"
        )
        button_2.place(
            x=435.0,
            y=187.0,
            width=192.0,
            height=57.0
        )

        # Create macOS-style close and minimize buttons
        close_button = tk.Button(
            self.window,
            text="●",
            font=("Helvetica", 25),  # Default font size
            fg="#FF5F56",
            bg="#000000",
            borderwidth=0,
            command=self.close_window,
            activebackground="#000000"
        )
        close_button.place(x=640, y=10, width=24, height=24)  # Position at the top right
        close_button.bind("<Enter>", self.on_enter_close)
        close_button.bind("<Leave>", self.on_leave_close)

        minimize_button = tk.Button(
            self.window,
            text="●",
            font=("Helvetica", 25),  # Default font size
            fg="#FFBD2E",
            bg="#000000",
            borderwidth=0,
            command=self.minimize_window,
            activebackground="#000000"
        )
        minimize_button.place(x=610, y=10, width=24, height=24)  # Position at the top right
        minimize_button.bind("<Enter>", self.on_enter_minimize)
        minimize_button.bind("<Leave>", self.on_leave_minimize)

        # Add status label for connection status
        self.status_label = tk.Label(
            self.window,
            text="Connecting to server...",
            bg="#000000",
            fg="#FFFF00",  # Yellow color for initial status
            font=self.create_custom_font(12)
        )
        self.status_label.place(x=435.0, y=250)  # Adjust the position as needed

        # Disable window resizing
        self.window.resizable(False, False)
        self.window.mainloop()

    def relative_to_assets(self, path: str) -> str:
        return os.path.join(self.ASSETS_PATH, path)

    def create_custom_font(self, size):
        return tk.font.Font(family="Anybody Regular", size=size)

    def close_window(self):
        self.window.destroy()

    def minimize_window(self):
        self.window.overrideredirect(False)
        self.window.iconify()

    def restore_window(self, event):
        if self.window.state() == 'normal':
            self.window.overrideredirect(True )

    def start_move(self, event):
        self.window.x = event.x
        self.window.y = event.y

    def stop_move(self, event):
        self.window.x = None
        self.window.y = None

    def on_motion(self, event):
        x = (event.x_root - self.window.x)
        y = (event.y_root - self.window.y)
        self.window.geometry(f"+{x}+{y}")

    def load_image(self, image_path):
        img = Image.open(image_path)
        img = img.convert("RGBA")  # Ensure image is in RGBA mode (with transparency)
        return ImageTk.PhotoImage(img)

    def on_enter_close(self, event):
        event.widget.config(text="x", fg="#FFFFFF", font=("Helvetica", 14))

    def on_leave_close(self, event):
        event.widget.config(text="●", fg="#FF5F56", font=("Helvetica", 20))

    def on_enter_minimize(self, event):
        event.widget.config(text="-", fg="#FFFFFF", font=("Helvetica", 14))

    def on_leave_minimize(self, event):
        event.widget.config(text="●", fg="#FFBD2E", font=("Helvetica", 20))

    # Button click method
    def open_join_session(self):
        new_window = Toplevel(self.window)  # Open a new Toplevel window
        currentSession(new_window)  # Start the join session window
    

# To run the application
if __name__ == "__main__":
    app = openApp()