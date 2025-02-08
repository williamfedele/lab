import pyperclip
import platform
from pynput import keyboard
from pynput.keyboard import Key, Controller
import time


class TextInserter:
    def __init__(self):
        self.os_type = platform.system().lower()

        if self.os_type == "darwin":
            self.keyboard_controller = Controller()
        else:
            print("Text insertion is only supported on MacOS at the moment.")

    def insert_text(self, text):
        if self.os_type == "darwin":
            self._macos_insert(text)
        else:
            print("Text insertion is only supported on MacOS at the moment.")
            raise NotImplementedError

    def _macos_insert(self, text):
        # Store original clipboard
        original = pyperclip.paste()

        # Set new text and paste
        pyperclip.copy(text)
        with self.keyboard_controller.pressed(Key.cmd):
            self.keyboard_controller.tap("v")

        time.sleep(0.1)
        # Restore clipboard
        pyperclip.copy(original)
