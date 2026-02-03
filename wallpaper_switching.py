# =============================================================================
#                           wallpaper_switching.py
# =============================================================================
# Author:          Aniq Abbasi
# Date of Creation: 1/17/2026
# Version:         1.0
# License:         "Free for Enthusiasts"
# =============================================================================

import os
import time
import platform
import ctypes
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
import random
import sys

# --- User Configuration ---
# The path to your folder containing the wallpaper images.
# Example for Windows: "C:/Users/YourUser/Pictures/Wallpapers"
# Example for macOS/Linux: "/home/YourUser/Pictures/Wallpapers"
WALLPAPER_FOLDER = Path("./wallpapers")

# The time in seconds between each wallpaper change.
CHANGE_INTERVAL_SECONDS = 15
# --------------------------


class WallpaperCycler:
    # This class manages the entire wallpaper switching process.
    # It handles image selection, preparation, and application in a unique, phased sequence.

    def __init__(self, image_folder: Path, interval: int):
        # This method sets up the initial state of the cycler.
        self.image_paths = self._scan_for_images(image_folder)
        if not self.image_paths:
            print(f"Error: No images found in '{image_folder}'. Please add images and try again.")
            sys.exit(1)
        
        # Shuffle the list once at the start for a unique sequence each time the script runs.
        random.shuffle(self.image_paths)

        self.interval = interval
        self.history_log = []
        self.screen_width, self.screen_height = self._get_screen_resolution()
        self.temp_dir = Path("./temp_wallpapers")
        self.temp_dir.mkdir(exist_ok=True) # A temporary directory for resized images.

        # The Novel Phased Iterator Logic: two pointers that move through the list.
        # One starts at the beginning, the other starts in the middle.
        self.home_screen_pointer = 0
        self.lock_screen_pointer = len(self.image_paths) // 2

        # This check prevents overlap if there are only 1 or 2 images.
        if self.home_screen_pointer == self.lock_screen_pointer and len(self.image_paths) > 1:
            self.lock_screen_pointer = (self.lock_screen_pointer + 1) % len(self.image_paths)

    def _scan_for_images(self, folder: Path) -> list:
        # Scans the specified folder for supported image files (.jpg, .png, etc.).
        print(f"Scanning for images in: {folder.resolve()}")
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        return [p for p in folder.iterdir() if p.suffix.lower() in supported_extensions]

    def _get_screen_resolution(self):
        # Gets the primary screen resolution in a cross-platform way.
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw() # Hide the empty Tkinter window.
            width, height = root.winfo_screenwidth(), root.winfo_screenheight()
            root.destroy()
            return width, height
        except Exception:
            # Fallback if tkinter is missing or fails.
            print("Warning: Could not detect screen resolution. Using fallback 1920x1080.")
            return 1920, 1080

    def _prepare_image(self, original_path: Path) -> Path:
        # Resizes an image to fit the screen without distortion by adding black bars.
        screen_size = (self.screen_width, self.screen_height)
        img = Image.open(original_path)
        
        # This preserves the aspect ratio while scaling down.
        img.thumbnail(screen_size, Image.LANCZOS)
        
        # Create a new black background with the exact screen resolution.
        background = Image.new('RGB', screen_size, (0, 0, 0))
        
        # Calculate the position to paste the scaled image so it's centered.
        paste_x = (screen_size[0] - img.width) // 2
        paste_y = (screen_size[1] - img.height) // 2
        
        # Paste the scaled image onto the center of the black background.
        background.paste(img, (paste_x, paste_y))
        
        # Save this prepared image to our temporary directory.
        prepared_path = self.temp_dir / f"prepared_{original_path.name}"
        background.save(prepared_path, "PNG")
        
        return prepared_path

    def _set_wallpaper(self, image_path: Path, screen_type: str):
        # Sets the wallpaper using OS-specific commands.
        system = platform.system()
        prepared_image_path = self._prepare_image(image_path)
        abs_path = str(prepared_image_path.resolve())

        try:
            if system == "Windows":
                # For Windows, SPI_SETDESKWALLPAPER sets the desktop background.
                # NOTE: Programmatically changing the Windows LOCK SCREEN is very complex.
                # For simplicity, this script will only change the DESKTOP wallpaper.
                ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
            
            elif system == "Darwin": # macOS
                # For macOS, an AppleScript command sets the desktop picture.
                script = f'tell application "System Events" to set picture of every desktop to "{abs_path}"'
                subprocess.run(["osascript", "-e", script], check=True)

            elif system == "Linux":
                # For Linux (GNOME/Cinnamon), we use gsettings.
                if screen_type == "Lock Screen":
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.screensaver", "picture-uri", f"file://{abs_path}"], check=True)
                else: # Home Screen
                    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{abs_path}"], check=True)
            return True
        except Exception as e:
            print(f"\nError: Failed to set wallpaper on {system}. Details: {e}")
            return False

    def _select_next_wallpaper_pair(self) -> tuple[Path, Path]:
        # This is the core logic: gets the next pair of wallpapers and advances the pointers.
        home_wallpaper = self.image_paths[self.home_screen_pointer]
        lock_wallpaper = self.image_paths[self.lock_screen_pointer]
        
        # Advance the pointers for the next cycle, wrapping around if needed.
        self.home_screen_pointer = (self.home_screen_pointer + 1) % len(self.image_paths)
        self.lock_screen_pointer = (self.lock_screen_pointer + 1) % len(self.image_paths)
        
        # If the pointers happen to land on the same spot, push one forward again.
        if self.home_screen_pointer == self.lock_screen_pointer:
            self.lock_screen_pointer = (self.lock_screen_pointer + 1) % len(self.image_paths)
            
        return home_wallpaper, lock_wallpaper
        
    def _log_activity(self, screen_type: str, filename: str, start_time: datetime, end_time: datetime):
        # Adds a record of the wallpaper change to our history.
        self.history_log.append({
            "Screen": screen_type,
            "File": filename,
            "Start Time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def _display_log_table(self):
        # Clears the console and prints the history log in a neat table.
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 85)
        print(" " * 27 + "WALLPAPER_SWITCHING.PY - Live Log")
        print("=" * 85)
        
        headers = ["Screen", "Wallpaper File", "Display Start Time", "Display End Time"]
        
        # Calculate column widths dynamically for a clean look.
        col_widths = {
            "Screen": 12,
            "File": max([len(h["File"]) for h in self.history_log] + [len(headers[1])]),
            "Start Time": 20,
            "End Time": 20
        }

        # Print table header.
        header_line = (f"{headers[0]:<{col_widths['Screen']}} | "
                       f"{headers[1]:<{col_widths['File']}} | "
                       f"{headers[2]:<{col_widths['Start Time']}} | "
                       f"{headers[3]:<{col_widths['End Time']}}")
        print(header_line)
        print("-" * len(header_line))
        
        # Print log entries.
        for entry in self.history_log:
            row_line = (f"{entry['Screen']:<{col_widths['Screen']}} | "
                        f"{entry['File']:<{col_widths['File']}} | "
                        f"{entry['Start Time']:<{col_widths['Start Time']}} | "
                        f"{entry['End Time']:<{col_widths['End Time']}}")
            print(row_line)
            
        print("\n" + "=" * 85)
        print(f"Next change in {self.interval} seconds... (Press Ctrl+C to exit)")

    def start_cycling(self):
        # The main execution loop that runs continuously.
        print("""
██╗    ██╗ █████╗ ██╗     ██╗     ██████╗  █████╗ ██████╗ ███████╗██████╗ 
██║    ██║██╔══██╗██║     ██║     ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║ █╗ ██║███████║██║     ██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██║███╗██║██╔══██║██║     ██║     ██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
╚███╔███╔╝██║  ██║███████╗███████╗██║     ██║  ██║██║     ███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
                                                                            
███████╗██╗    ██╗██╗████████╗ ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗       
██╔════╝██║    ██║██║╚══██╔══╝██╔════╝██║  ██║██║████╗  ██║██╔════╝       
███████╗██║ █╗ ██║██║   ██║   ██║     ███████║██║██╔██╗ ██║██║  ███╗      
╚════██║██║███╗██║██║   ██║   ██║     ██╔══██║██║██║╚██╗██║██║   ██║      
███████║╚███╔███╔╝██║   ██║   ╚██████╗██║  ██║██║██║ ╚████║╚██████╔╝      
╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝       
""")
        print(f"--- Starting WALLPAPER_SWITCHING.PY ---")
        print(f"Found {len(self.image_paths)} images. Screen resolution: {self.screen_width}x{self.screen_height}.")
        time.sleep(2)

        try:
            while True:
                start_time = datetime.now()
                end_time = start_time + timedelta(seconds=self.interval)
                
                # Get the next pair of unique wallpapers.
                home_img, lock_img = self._select_next_wallpaper_pair()
                
                # Set Home Screen Wallpaper.
                self._set_wallpaper(home_img, "Home Screen")
                self._log_activity("Home Screen", home_img.name, start_time, end_time)
                
                # Set Lock Screen Wallpaper.
                self._set_wallpaper(lock_img, "Lock Screen")
                self._log_activity("Lock Screen", lock_img.name, start_time, end_time)
                
                # Update the display with the new log entries.
                self._display_log_table()
                
                # Wait for the specified interval.
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\nScript stopped by user. Cleaning up temporary files...")
            # Clean up the temporary directory on exit.
            for temp_file in self.temp_dir.iterdir():
                temp_file.unlink()
            self.temp_dir.rmdir()
            print("Cleanup complete. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            sys.exit(1)


if __name__ == "__main__":
    # Create an instance of our cycler and start the process.
    cycler = WallpaperCycler(
        image_folder=WALLPAPER_FOLDER,
        interval=CHANGE_INTERVAL_SECONDS
    )
    cycler.start_cycling()