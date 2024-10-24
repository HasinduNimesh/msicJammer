from pathlib import Path
from tkinter import Tk, Canvas, Button, Label, Toplevel
from PIL import Image, ImageTk  # Import PIL modules for images
import tkinter.font as tkFont

class MusicJammerApp:
    def __init__(self):
        # Paths to resources
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / "assets" / "frame0"

        # Initialize the window
        self.window = Tk()
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
        font_path = self.ASSETS_PATH / "Anybody-Regular.ttf"
        self.window.tk.call('font', 'create', 'AnybodyRegular', '-family', 'Anybody Regular', '-size', '10', '-weight', 'normal')
        self.window.tk.call('font', 'configure', 'AnybodyRegular', '-family', 'Anybody Regular', '-size', '10', '-weight', 'normal')

        # Bind the window dragging functions
        self.window.bind("<ButtonPress-1>", self.start_move)
        self.window.bind("<ButtonRelease-1>", self.stop_move)
        self.window.bind("<B1-Motion>", self.on_motion)
        self.window.bind("<Map>", self.restore_window)

        # Create a canvas to hold elements
        self.canvas = Canvas(
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
        image_1 = self.load_image(self.relative_to_assets("image_1.png"))
        self.canvas.create_image(
            224.0,
            375.0,
            image=image_1
        )

        # Button 1 with PIL to handle transparency
        button_image_1 = self.load_image(self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_1 clicked"),
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
        button_image_2 = self.load_image(self.relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
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
        close_button = Button(
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

        minimize_button = Button(
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

        # Disable window resizing
        self.window.resizable(False, False)
        self.window.mainloop()

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def create_custom_font(self, size):
        return tkFont.Font(family="Anybody Regular", size=size)

    def close_window(self):
        self.window.destroy()

    def minimize_window(self):
        self.window.overrideredirect(False)
        self.window.iconify()

    def restore_window(self, event):
        if self.window.state() == 'normal':
            self.window.overrideredirect(True)

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

# To run the application
if __name__ == "__main__":
    app = MusicJammerApp()