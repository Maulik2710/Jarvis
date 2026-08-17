# ui/neuro_ball.py
import tkinter as tk
import math

class NeuroBallWidget:
    def __init__(self, size=180):
        self.size = size
        self.state = "LISTENING"
        self.phase = 0.0
        self.on_click_callback = None
        self.is_alive = True  # Tracks whether the window is still open

        # Create frameless, transparent, always-on-top window
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "#000001")
        self.root.config(bg="#000001")

        # Position at bottom-right corner
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - self.size - 30
        y = screen_h - self.size - 60
        self.root.geometry(f"{self.size}x{self.size}+{x}+{y}")

        # Canvas configuration
        self.canvas = tk.Canvas(
            self.root, 
            width=self.size, 
            height=self.size, 
            bg="#000001", 
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._handle_click)

        self._animate()

    def set_on_click(self, callback):
        self.on_click_callback = callback

    def _handle_click(self, event):
        if self.on_click_callback:
            self.on_click_callback()

    def set_state(self, state: str):
        self.state = state.upper()

    def _get_color_palette(self):
        if self.state == "LISTENING":
            return {
                "outer_aura": "#2b1055",
                "mid_glow": "#6d28d9",
                "core_wave": "#818cf8",
                "highlight": "#c7d2fe",
                "pure_bright": "#ffffff"
            }
        elif self.state == "THINKING":
            return {
                "outer_aura": "#3b0764",
                "mid_glow": "#a21caf",
                "core_wave": "#e879f9",
                "highlight": "#f5d0fe",
                "pure_bright": "#ffffff"
            }
        elif self.state == "SPEAKING":
            return {
                "outer_aura": "#042f2e",
                "mid_glow": "#0f766e",
                "core_wave": "#2dd4bf",
                "highlight": "#99f6e4",
                "pure_bright": "#ffffff"
            }
        elif self.state == "SLEEP":
            return {
                "outer_aura": "#0f172a",
                "mid_glow": "#1e293b",
                "core_wave": "#334155",
                "highlight": "#475569",
                "pure_bright": "#64748b"
            }
        else:
            return {
                "outer_aura": "#1e1b4b",
                "mid_glow": "#3730a3",
                "core_wave": "#4f46e5",
                "highlight": "#a5b4fc",
                "pure_bright": "#e0e7ff"
            }

    def _animate(self):
        # Stop animation immediately if widget has been destroyed
        if not self.is_alive:
            return

        try:
            self.canvas.delete("all")
            
            cx = self.size // 2
            cy = self.size // 2
            base_radius = (self.size // 2) - 30
            
            if self.state == "THINKING":
                speed, wave_amp, harmonics = 0.14, 8.0, 5
            elif self.state == "SPEAKING":
                speed, wave_amp, harmonics = 0.10, 11.0, 4
            elif self.state == "LISTENING":
                speed, wave_amp, harmonics = 0.06, 6.0, 3
            elif self.state == "SLEEP":
                speed, wave_amp, harmonics = 0.01, 1.0, 2
            else:
                speed, wave_amp, harmonics = 0.03, 3.0, 3

            self.phase += speed
            palette = self._get_color_palette()

            layers = [
                {"width": 8, "color": palette["outer_aura"], "amp_mult": 1.4, "freq": harmonics,     "phase_off": 0.0},
                {"width": 5, "color": palette["mid_glow"],   "amp_mult": 1.1, "freq": harmonics + 1, "phase_off": 1.2},
                {"width": 3, "color": palette["core_wave"],  "amp_mult": 0.9, "freq": harmonics,     "phase_off": 2.5},
                {"width": 1.5, "color": palette["highlight"],"amp_mult": 0.7, "freq": harmonics + 2, "phase_off": 3.8}
            ]

            steps = 100
            for layer in layers:
                points = []
                for i in range(steps + 1):
                    theta = (i / steps) * 2 * math.pi
                    r_offset = math.sin(layer["freq"] * theta + self.phase + layer["phase_off"]) * (wave_amp * layer["amp_mult"])
                    r_offset += math.cos((layer["freq"] - 1) * theta - self.phase) * (wave_amp * 0.4)
                    
                    r = base_radius + r_offset
                    x = cx + r * math.cos(theta)
                    y = cy + r * math.sin(theta)
                    points.extend([x, y])

                self.canvas.create_line(
                    points, 
                    fill=layer["color"], 
                    width=layer["width"], 
                    smooth=True, 
                    splinesteps=12,
                    joinstyle=tk.ROUND
                )

            if self.state != "SLEEP":
                accent_pts = []
                for i in range(steps + 1):
                    theta = (i / steps) * 2 * math.pi
                    r_offset = math.sin(3 * theta + self.phase) * (wave_amp * 0.6)
                    r = base_radius + r_offset
                    x = cx + r * math.cos(theta)
                    y = cy + r * math.sin(theta)
                    accent_pts.extend([x, y])
                
                self.canvas.create_line(
                    accent_pts, 
                    fill=palette["pure_bright"], 
                    width=1, 
                    smooth=True, 
                    splinesteps=12
                )

            # Schedule next frame if alive
            if self.is_alive:
                self.root.after(33, self._animate)

        except (tk.TclError, Exception):
            # Window was closed during animation cycle
            self.is_alive = False

    def run(self):
        self.root.mainloop()

    def close(self):
        self.is_alive = False
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass