import pyperclip
import tkinter as tk
from tkinter import ttk
import json
import requests
from threading import Thread
from PIL import Image, ImageDraw
import pystray
import threading
from tkinter import messagebox
from pynput import keyboard
from openai import OpenAI
import subprocess
from text_inserter import TextInserter


def get_current_app():
    """Return the name of the current frontmost app using AppleScript."""
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    return subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()


def return_focus_to_previous_app(prev_app):
    """Use AppleScript to bring the previous app back to the front."""
    script = f'tell application "{prev_app}" to activate'
    subprocess.run(["osascript", "-e", script])


prev_app = None


class TextAssistant:
    def __init__(self):
        # Initialize configuration
        self.config = {
            "shortcut": "ctrl+shift+space",
            "api_key": "ollama",
            "api_url": "http://localhost:11434/v1/",
            "model": "llama3.2:latest",
            "max_tokens": 1000,
            "use_direct_insertion": True,
            "minimize_to_tray": True,
        }
        self.load_config()

        # Initialize text inserter
        self.text_inserter = (
            TextInserter()
        )  # Assuming TextInserter class from previous code

        # Initialize main window (hidden by default)
        self.root = tk.Tk()
        self.root.withdraw()
        self.setup_ui()

        # Create system tray icon
        self.create_tray_icon()

        self.current_keys = set()

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key):
        try:
            # Add the pressed key to our set
            if hasattr(key, "char"):
                self.current_keys.add(key.char)
            else:
                self.current_keys.add(key)

            # Check if our combination is pressed (cmd+shift+space)
            if (
                keyboard.Key.cmd in self.current_keys
                and keyboard.Key.shift in self.current_keys
                and keyboard.Key.space in self.current_keys
            ):
                self.root.after(0, self.activate_assistant)
        except Exception as e:
            print(f"Error in on_press: {e}")

    def on_release(self, key):
        try:
            # Remove released keys from our set
            if hasattr(key, "char"):
                self.current_keys.discard(key.char)
            else:
                self.current_keys.discard(key)
        except Exception as e:
            print(f"Error in on_release: {e}")

    def create_tray_icon(self):
        # Create a simple icon (you might want to replace this with a proper icon file)
        icon_size = 64
        icon_image = Image.new("RGB", (icon_size, icon_size), color="white")
        draw = ImageDraw.Draw(icon_image)
        draw.rectangle([8, 8, icon_size - 8, icon_size - 8], fill="black")

        # Create menu
        menu = (
            pystray.MenuItem("Settings", self.show_settings_from_tray),
            pystray.MenuItem("About", self.show_about),
            pystray.MenuItem("Exit", self.quit_app),
        )

        # Create system tray icon
        self.icon = pystray.Icon("text_assistant", icon_image, "Text Assistant", menu)

        # Start icon in a separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_settings_from_tray(self):
        self.root.after(0, self.show_settings)

    def show_settings(self):
        def save_callback(new_config):
            self.config.update(new_config)
            self.save_config()
            # Re-register shortcut if it changed
            if new_config["shortcut"] != self.config["shortcut"]:
                self.register_shortcut()

        # Run settings window in main thread
        self.root.after(0, lambda: SettingsWindow(self.config, save_callback))

    def show_about(self):
        messagebox.showinfo(
            "About Text Assistant",
            "Text Assistant v1.0\n\n"
            "A tool for quick LLM interactions.\n"
            "Use the global shortcut (default: Ctrl+Shift+Space) to activate.",
        )

    def quit_app(self):
        self.icon.stop()
        self.root.quit()

    def register_shortcut(self):
        # Remove existing shortcut if any
        try:
            keyboard.remove_hotkey(self.config["shortcut"])
        except:
            pass
        # Register new shortcut
        keyboard.add_hotkey(self.config["shortcut"], self.activate_assistant)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                saved_config = json.load(f)
                self.config.update(saved_config)
        except FileNotFoundError:
            self.save_config()

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f)

    def setup_ui(self):
        # Create query window
        self.query_window = tk.Toplevel(self.root)
        self.query_window.withdraw()
        self.query_window.title("Ask about selected text")

        # Make window float on top
        self.query_window.attributes("-topmost", True)

        # Add query input
        self.query_frame = ttk.Frame(self.query_window, padding="10")
        self.query_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.query_label = ttk.Label(self.query_frame, text="Your question:")
        self.query_label.grid(row=0, column=0, sticky=tk.W)

        self.query_entry = ttk.Entry(self.query_frame, width=50)
        self.query_entry.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.query_entry.bind("<Return>", self.handle_query)

        # Add insertion mode toggle
        self.insertion_var = tk.BooleanVar(value=self.config["use_direct_insertion"])
        self.insertion_check = ttk.Checkbutton(
            self.query_frame,
            text="Use direct insertion",
            variable=self.insertion_var,
            command=self.toggle_insertion_mode,
        )
        self.insertion_check.grid(row=2, column=0, sticky=tk.W)

        # Add status label
        self.status_label = ttk.Label(self.query_frame, text="")
        self.status_label.grid(row=3, column=0, sticky=tk.W)

    def toggle_insertion_mode(self):
        self.config["use_direct_insertion"] = self.insertion_var.get()
        self.save_config()

    def activate_assistant(self):
        # Get current app
        global prev_app
        prev_app = get_current_app()

        # Get clipboard content
        self.context = pyperclip.paste()

        # Position window near cursor, taking into account screen boundaries
        cursor_x = self.root.winfo_pointerx()
        cursor_y = self.root.winfo_pointery()
        window_width = self.query_window.winfo_reqwidth()
        window_height = self.query_window.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate new position
        x = min(cursor_x + 100, screen_width - window_width)
        y = min(cursor_y + 100, screen_height - window_height)

        self.query_window.geometry(f"+{x}+{y}")

        # Show window and focus
        self.query_window.deiconify()
        self.query_window.focus_force()
        self.query_entry.focus_set()
        self.query_entry.delete(0, tk.END)

    def handle_query(self, event=None):
        query = self.query_entry.get()
        if not query:
            return

        # Clear entry and show status
        self.query_entry.delete(0, tk.END)
        self.status_label.config(text="Processing...")

        # Process in background
        Thread(target=self.process_query, args=(query,)).start()

    def process_query(self, query):
        try:
            client = OpenAI(
                base_url=self.config["api_url"], api_key=self.config["api_key"]
            )

            request = {
                "model": self.config["model"],
                "messages": [
                    {
                        "role": "user",
                        "content": f"Context: {self.context}\n\nQuestion: {query}",
                    }
                ],
                "max_tokens": self.config["max_tokens"],
                "temperature": 0,
            }

            try:
                # put focus back on the previous app
                self.query_window.after(
                    0, lambda: return_focus_to_previous_app(prev_app)
                )

                response = client.chat.completions.create(**request)

                if response:
                    result = response.choices[0].message.content

                    if self.config["use_direct_insertion"] and not prev_app is None:
                        try:
                            self.text_inserter.insert_text(result)
                            self.status_label.config(text="Response inserted!")
                        except Exception as e:
                            pyperclip.copy(result)
                            self.status_label.config(
                                text="Insertion failed - copied to clipboard instead"
                            )
                    else:
                        pyperclip.copy(result)
                        self.status_label.config(text="Response copied to clipboard!")
                else:
                    self.status_label.config(
                        text=f"Error: API request failed ({response.status_code})"
                    )

            except Exception as e:
                print(f"OpenAI API Error: {e}")  # Print the specific OpenAI error
                self.status_label.config(text=f"Error: OpenAI API failed: {str(e)}")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

        self.query_window.after(2000, self.query_window.withdraw)

    def run(self):
        self.root.mainloop()
