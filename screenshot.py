"""
Script written by Aniq Abbasi A Student of BS AI at Institute of Space and Technology.
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFilter
from datetime import datetime
import keyboard
import os
import sys

SAVE_PATH = r"C:\Users\hp\OneDrive\Pictures\Screenshots"

class FreehandScreenshotTool:
    
    def __init__(self):
        self.is_capturing = False
        self.points = []
        self.lines = []
        self.screenshot = None
        self.root = None
        self.canvas = None
        
        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)
    
    def capture(self):
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.points = []
        self.lines = []
        
        self.screenshot = ImageGrab.grab()
        
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.update()
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        self.root.deiconify()
        self.root.overrideredirect(True)
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        dim_screenshot = self.screenshot.copy()
        dim_screenshot = Image.blend(dim_screenshot.convert('RGBA'), Image.new('RGBA', dim_screenshot.size, (0, 0, 0, 180)), 0.5)
        self.bg_photo = ImageTk.PhotoImage(dim_screenshot)
        self.canvas.create_image(0, 0, anchor='nw', image=self.bg_photo)
        
        self.canvas.create_text(
            screen_w // 2, 50,
            text="Draw around area to capture  |  Shift+U = Cancel  |  Shift+Q = Quit",
            font=("Arial", 16, "bold"),
            fill="#00FF00"
        )
        
        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        
        self.check_keys()
        self.root.mainloop()
    
    def check_keys(self):
        if keyboard.is_pressed('shift+u'):
            self.cancel()
            return
        if keyboard.is_pressed('shift+q'):
            self.quit_app()
            return
        if self.root:
            self.root.after(50, self.check_keys)
    
    def mouse_down(self, e):
        self.points = [(e.x, e.y)]
        for line in self.lines:
            self.canvas.delete(line)
        self.lines = []
    
    def mouse_move(self, e):
        if self.points:
            self.points.append((e.x, e.y))
            if len(self.points) >= 2:
                line = self.canvas.create_line(
                    self.points[-2][0], self.points[-2][1],
                    self.points[-1][0], self.points[-1][1],
                    fill='#00FF00', width=3
                )
                self.lines.append(line)
    
    def mouse_up(self, e):
        if len(self.points) < 10:
            self.free_screen()
            return
        
        self.points.append(self.points[0])
        self.save_screenshot()
        self.free_screen()
    
    def save_screenshot(self):
        if len(self.points) < 3:
            return
        
        try:
            w, h = self.screenshot.size
            
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.polygon(self.points, fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(1))
            
            output = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            output.paste(self.screenshot.convert('RGBA'), mask=mask)
            
            x1 = max(0, min(p[0] for p in self.points) - 10)
            y1 = max(0, min(p[1] for p in self.points) - 10)
            x2 = min(w, max(p[0] for p in self.points) + 10)
            y2 = min(h, max(p[1] for p in self.points) + 10)
            
            output = output.crop((x1, y1, x2, y2))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(SAVE_PATH, f"screenshot_{timestamp}.png")
            output.save(filepath, "PNG")
        except:
            pass
    
    def free_screen(self):
        self.is_capturing = False
        self.points = []
        self.lines = []
        self.screenshot = None
        if self.root:
            self.root.destroy()
            self.root = None
    
    def cancel(self):
        self.free_screen()
    
    def quit_app(self):
        self.free_screen()
        keyboard.unhook_all()
        sys.exit(0)


app = FreehandScreenshotTool()

keyboard.add_hotkey('shift+a', app.capture)
keyboard.add_hotkey('shift+u', app.cancel)
keyboard.add_hotkey('shift+q', app.quit_app)

keyboard.wait('shift+q')