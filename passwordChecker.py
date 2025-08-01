import tkinter as tk
from tkinter import ttk
import string
import math
import random
from pathlib import Path

# --- Constants ---
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-=_+[]{}|;:',.<>/?"
CRACKING_SPEED_PER_SECOND = 1e12
MAX_ENTROPY_GAUGE = 128  # The entropy value that corresponds to the gauge's max reading

class PasswordDashboard:
    """A password strength checker with a graphical dashboard UI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Password Security Dashboard")
        self.root.geometry("850x600") # Increased size for better readability
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")
        self.wordlist_words = set()

        # --- Style Configuration ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Segoe UI", 10))
        style.configure("TFrame", background="#2c3e50")
        style.configure("Right.TFrame", background="#34495e")
        style.configure("TLabelframe", background="#34495e", bordercolor="#2c3e50")
        style.configure("TLabelframe.Label", background="#34495e", foreground="#ecf0f1", font=("Segoe UI", 10, "bold"))

        self._create_widgets()
        self._scan_for_wordlists()
        self._update_gauge(0, initial=True) # Draw the initial empty gauge

    def _create_widgets(self):
        # Main layout frames
        left_panel = ttk.Frame(self.root, padding=25)
        left_panel.pack(side="left", fill="both", expand=True)
        right_panel = ttk.Frame(self.root, padding=30, style="Right.TFrame")
        right_panel.pack(side="right", fill="both")

        self._create_left_panel(left_panel)
        self._create_right_panel(right_panel)

    def _create_left_panel(self, parent):
        # Password Entry
        self.password_entry = ttk.Entry(parent, font=("Segoe UI", 14))
        self.password_entry.pack(fill="x", pady=(10, 25))
        self.password_entry.bind("<KeyRelease>", self._on_password_change)

        # Security Dial Canvas
        self.gauge_canvas = tk.Canvas(parent, width=420, height=230, bg="#2c3e50", highlightthickness=0)
        self.gauge_canvas.pack(pady=10)

        # Character Set Checklist
        checklist_frame = ttk.Frame(parent, padding=10)
        checklist_frame.pack(pady=25, fill="x")
        checklist_frame.columnconfigure((0, 1, 2, 3), weight=1)
        self.check_lower = self._create_check_label(checklist_frame, "a-z Lowercase", 0)
        self.check_upper = self._create_check_label(checklist_frame, "A-Z Uppercase", 1)
        self.check_digits = self._create_check_label(checklist_frame, "0-9 Numbers", 2)
        self.check_symbols = self._create_check_label(checklist_frame, "#$& Symbols", 3)

    def _create_right_panel(self, parent):
        # Status
        self.status_label = ttk.Label(parent, text="AWAITING INPUT", font=("Segoe UI", 24, "bold"), anchor="center", foreground="#bdc3c7")
        self.status_label.pack(pady=(20, 5), fill="x")

        # Crack Time
        self.crack_time_label = ttk.Label(parent, text="Est. Crack Time: -", font=("Segoe UI", 11), anchor="center")
        self.crack_time_label.pack(pady=5, fill="x")

        # Wordlist Frame
        self.wordlist_frame = ttk.LabelFrame(parent, text="Breach Check", padding=10)
        self.wordlist_frame.pack(pady=25, fill="x")
        self.wordlist_combo = ttk.Combobox(self.wordlist_frame, state="readonly", font=("Segoe UI", 9))
        self.wordlist_combo.pack(fill="x")
        self.wordlist_combo.bind("<<ComboboxSelected>>", self._load_selected_wordlist)
        self.wordlist_status = ttk.Label(self.wordlist_frame, text="No wordlists found", font=("Segoe UI", 8), foreground="#7f8c8d")
        self.wordlist_status.pack(fill="x", pady=(5,0))

        # Recommendations
        self.reco_label = ttk.Label(parent, text="Start typing a password to see recommendations.", font=("Segoe UI", 10), wraplength=320, justify="center")
        self.reco_label.pack(pady=20, fill="both", expand=True)

    def _create_check_label(self, parent, text, col):
        label = ttk.Label(parent, text=text, font=("Segoe UI", 10), foreground="#7f8c8d")
        label.grid(row=0, column=col, padx=5, sticky="ew")
        return label

    def _on_password_change(self, event=None):
        password = self.password_entry.get()
        if ' ' in password:
            self._set_ui_state("invalid")
            return
        if not password:
            self._set_ui_state("default")
            return
        if self.wordlist_words and password in self.wordlist_words:
            self._set_ui_state("compromised", password)
            return
        self._set_ui_state("analyzing", password)

    def _set_ui_state(self, state, password=""):
        pool_size, used_sets = self._get_charset_info(password)
        entropy = len(password) * math.log2(pool_size) if pool_size > 1 else 0
        self._update_checklist(used_sets)

        if state == "invalid":
            self.status_label.config(text="INVALID", foreground="#e67e22")
            self.crack_time_label.config(text="Spaces are not allowed")
            self.reco_label.config(text="Please remove spaces to continue analysis.")
            self._update_gauge(0, error_state=True)
        elif state == "default":
            self.status_label.config(text="AWAITING INPUT", foreground="#bdc3c7")
            self.crack_time_label.config(text="Est. Crack Time: -")
            self.reco_label.config(text="Start typing a password to see recommendations.")
            self._update_gauge(0)
        elif state == "compromised":
            self.status_label.config(text="COMPROMISED", foreground="#e74c3c")
            self.crack_time_label.config(text="Est. Crack Time: INSTANT")
            self.reco_label.config(text="This password is in a known data breach. It offers no security and must not be used.")
            self._update_gauge(entropy, error_state=True)
        elif state == "analyzing":
            combinations = pool_size ** len(password)
            time_to_crack_sec = combinations / CRACKING_SPEED_PER_SECOND
            self.crack_time_label.config(text=f"Est. Crack Time: {self._format_time(time_to_crack_sec)}")

            strength_text, color = self._get_strength_level(entropy)
            self.status_label.config(text=strength_text, foreground=color)
            self.reco_label.config(text=self._get_recommendations(len(password), used_sets))
            self._update_gauge(entropy)

    def _update_gauge(self, entropy, initial=False, error_state=False):
        canvas = self.gauge_canvas
        canvas.delete("all")
        w, h = 420, 230
        cx, cy = w / 2, h - 20

        # **FIXED**: Gauge colors now go from red (left) to green (right).
        colors = [("#e74c3c", 0.4), ("#f39c12", 0.25), ("#f1c40f", 0.15), ("#2ecc71", 0.2)]
        # The start angle for create_arc is 3 o'clock. We draw from 180 (left) to 0 (right).
        start = 180
        for color, extent_frac in colors:
            extent = -180 * extent_frac # Negative extent draws clockwise
            canvas.create_arc(20, 20, w - 20, h * 2 - 40, start=start, extent=extent,
                              style="arc", outline=color, width=25)
            start += extent
        
        canvas.create_text(45, h - 35, text="Weak", font=("Segoe UI", 9), fill="#7f8c8d")
        canvas.create_text(w - 45, h - 35, text="Strong", font=("Segoe UI", 9), fill="#7f8c8d")

        # Needle moves from left (weak) to right (strong)
        entropy_ratio = min(entropy / MAX_ENTROPY_GAUGE, 1.0)
        angle = (1 - entropy_ratio) * math.pi
        needle_len = cx - 55
        nx = cx + needle_len * math.cos(angle)
        ny = cy - needle_len * math.sin(angle)
        
        needle_color = "#e74c3c" if error_state else "#ecf0f1"
        canvas.create_line(cx, cy, nx, ny, width=3, fill=needle_color, arrow=tk.LAST)
        canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=needle_color, outline="")

    def _update_checklist(self, used_sets):
        active_color, inactive_color = "#2ecc71", "#7f8c8d"
        self.check_lower.config(foreground=active_color if "Lowercase" in used_sets else inactive_color,
                                text="✔ Lowercase" if "Lowercase" in used_sets else "a-z Lowercase")
        self.check_upper.config(foreground=active_color if "Uppercase" in used_sets else inactive_color,
                                text="✔ Uppercase" if "Uppercase" in used_sets else "A-Z Uppercase")
        self.check_digits.config(foreground=active_color if "Numbers" in used_sets else inactive_color,
                                 text="✔ Numbers" if "Numbers" in used_sets else "0-9 Numbers")
        self.check_symbols.config(foreground=active_color if "Symbols" in used_sets else inactive_color,
                                  text="✔ Symbols" if "Symbols" in used_sets else "#$& Symbols")

    def _scan_for_wordlists(self):
        wordlist_dir = Path("wordlists")
        if not wordlist_dir.is_dir():
            self.wordlist_frame.pack_forget()
            return
        txt_files = [str(p) for p in wordlist_dir.rglob("*.txt")]
        if txt_files:
            self.wordlist_combo['values'] = txt_files
            self.wordlist_combo.current(0)
            self._load_selected_wordlist()
        else:
            self.wordlist_combo.set("No .txt files found")
            self.wordlist_combo.config(state="disabled")

    def _load_selected_wordlist(self, event=None):
        filepath = self.wordlist_combo.get()
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.wordlist_words = {line.strip() for line in f if line.strip()}
            self.wordlist_status.config(text=f"Loaded {len(self.wordlist_words):,} words", foreground="#2ecc71")
            self._on_password_change()
        except Exception:
            self.wordlist_status.config(text="Error loading file", foreground="#e74c3c")
            self.wordlist_words.clear()

    @staticmethod
    def _get_charset_info(password):
        used_sets = set()
        if any(c in LOWERCASE for c in password): used_sets.add("Lowercase")
        if any(c in UPPERCASE for c in password): used_sets.add("Uppercase")
        if any(c in DIGITS for c in password): used_sets.add("Numbers")
        if any(c in SYMBOLS for c in password): used_sets.add("Symbols")
        pool_size = (len(LOWERCASE) if "Lowercase" in used_sets else 0) + \
                    (len(UPPERCASE) if "Uppercase" in used_sets else 0) + \
                    (len(DIGITS) if "Numbers" in used_sets else 0) + \
                    (len(SYMBOLS) if "Symbols" in used_sets else 0)
        return pool_size, used_sets

    @staticmethod
    def _get_strength_level(entropy):
        if entropy < 35: return "VERY WEAK", "#e74c3c"
        if entropy < 60: return "WEAK", "#f39c12"
        if entropy < 80: return "MODERATE", "#f1c40f"
        if entropy < 100: return "STRONG", "#2ecc71"
        return "VERY STRONG", "#1abc9c"

    @staticmethod
    def _get_recommendations(length, used_sets):
        recos = []
        if length < 12: recos.append("• Make your password longer (16+ characters is recommended).")
        if len(used_sets) < 4: recos.append("• Add more character types (uppercase, numbers, symbols).")
        if not recos: return "This is an excellent password. Well done."
        return "\n".join(recos)

    @staticmethod
    def _format_time(seconds):
        if seconds < 1e-9: return "instantly"
        if seconds < 1: return f"~{seconds * 1e3:.0f} milliseconds"
        if seconds < 60: return f"~{seconds:.1f} seconds"
        minutes, hours, days = seconds / 60, seconds / 3600, seconds / 86400
        if minutes < 60: return f"~{minutes:.1f} minutes"
        if hours < 24: return f"~{hours:.1f} hours"
        if days < 365.25: return f"~{days:.0f} days"
        years = days / 365.25
        if years < 1e3: return f"~{years:,.0f} years"
        if years < 1e6: return f"~{years / 1e3:,.0f} thousand years"
        if years < 1e9: return f"~{years / 1e6:,.0f} million years"
        return "eons"

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordDashboard(root)
    root.mainloop()
