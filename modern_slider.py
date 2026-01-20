"""
Modern Slider Widget v4 - High Performance & Polish
"""
import tkinter as tk
import time

class ModernSlider(tk.Canvas):
    def __init__(self, parent, from_=0, to=100, **kwargs):
        self.var = kwargs.pop('variable', tk.DoubleVar())
        self.command = kwargs.pop('command', None)
        
        # Throttling settings
        self.last_update = 0
        self.update_delay = 0.016  # ~60 FPS update limit
        
        # Wymiary
        self.thumb_r = 7
        self.track_h = 3
        self.margin = 12
        canvas_h = self.thumb_r * 2 + 6
        
        super().__init__(parent, height=canvas_h, bg="#16161A", highlightthickness=0, cursor="hand2", **kwargs)
        
        self.from_ = from_
        self.to = to
        self.dragging = False
        self.hover = False
        
        self.track_bg = "#2a2a2a"
        self.track_fill = "#00ADB5"
        self.thumb_bg = "#ffffff"
        self.thumb_border = "#00ADB5"
        
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        
        self.var.trace_add("write", lambda *a: self._redraw())
        self.after(50, self._redraw)
    
    def _set_hover(self, state):
        self.hover = state
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 40: return
        
        center_y = h // 2
        track_l = self.margin
        track_r = w - self.margin
        tw = track_r - track_l
        
        # Track Background
        self.create_line(track_l, center_y, track_r, center_y, fill=self.track_bg, width=self.track_h, capstyle="round")
        
        # Calculate Position
        val = self.var.get()
        ratio = (val - self.from_) / (self.to - self.from_) if self.to != self.from_ else 0
        ratio = max(0, min(1, ratio))
        tx = track_l + ratio * tw
        
        # Track Fill
        if tx > track_l:
            self.create_line(track_l, center_y, tx, center_y, fill=self.track_fill, width=self.track_h, capstyle="round")
        
        # Thumb
        r = self.thumb_r
        # Subtelny cień (ciemniejszy barwnik bez ziarnistości)
        self.create_oval(tx-r+1, center_y-r+1, tx+r+1, center_y+r+1, fill="#0a0a0d", outline="")
        # Główne kółko - perfekcyjnie gładkie
        clr_border = "#00FFFF" if self.hover else self.track_fill
        self.create_oval(tx-r, center_y-r, tx+r, center_y+r, fill=self.thumb_bg, outline=clr_border, width=2)

    def _value_from_x(self, x):
        w = self.winfo_width()
        tw = w - 2 * self.margin
        ratio = max(0, min(1, (x - self.margin) / tw))
        return self.from_ + ratio * (self.to - self.from_)

    def _on_press(self, event):
        self.dragging = True
        self._update_value(event.x)

    def _on_drag(self, event):
        if self.dragging:
            self._update_value(event.x, throttled=True)

    def _on_release(self, event):
        self.dragging = False
        self._update_value(event.x) # Final update

    def _update_value(self, x, throttled=False):
        new_val = self._value_from_x(x)
        self.var.set(new_val)
        
        now = time.time()
        if not throttled or (now - self.last_update) > self.update_delay:
            self.last_update = now
            if self.command:
                self.command(new_val)
        self._redraw()

    def set(self, value):
        self.var.set(value)
        self._redraw()

    def get(self):
        return self.var.get()

