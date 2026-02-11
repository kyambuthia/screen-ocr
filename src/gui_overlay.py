import threading
import time
import tkinter as tk
from tkinter import messagebox

import pyperclip
from dotenv import load_dotenv

from capture_ocr import run_ocr


class OcrOverlayApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.last_text = ""
        self.is_busy = False

        self.root.title("Screen OCR")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="#111111")
        self.root.geometry("320x180+40+40")

        self.frame = tk.Frame(root, bg="#111111", bd=1, relief="solid", highlightthickness=0)
        self.frame.pack(fill="both", expand=True)

        self.title_bar = tk.Frame(self.frame, bg="#1b1b1b", height=28)
        self.title_bar.pack(fill="x")
        self.title_label = tk.Label(
            self.title_bar,
            text="Screen OCR",
            fg="#f2f2f2",
            bg="#1b1b1b",
            font=("Segoe UI", 9, "bold"),
        )
        self.title_label.pack(side="left", padx=8)
        self.close_btn = tk.Button(
            self.title_bar,
            text="x",
            command=self.root.destroy,
            fg="#dddddd",
            bg="#1b1b1b",
            activebackground="#2a2a2a",
            activeforeground="#ffffff",
            bd=0,
            padx=8,
            pady=0,
        )
        self.close_btn.pack(side="right")

        self.canvas = tk.Canvas(
            self.frame,
            width=300,
            height=88,
            bg="#111111",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(pady=(8, 2))

        self.capture_circle = self._draw_circle_button(85, 44, 30, "Capture", "#2f8f6b")
        self.copy_circle = self._draw_circle_button(215, 44, 30, "Copy", "#3478d9")

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.frame,
            textvariable=self.status_var,
            fg="#d2d2d2",
            bg="#111111",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(pady=(2, 4))

        self.output = tk.Text(
            self.frame,
            height=3,
            wrap="word",
            bg="#181818",
            fg="#e8e8e8",
            insertbackground="#e8e8e8",
            relief="flat",
            padx=6,
            pady=6,
        )
        self.output.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.canvas.bind("<Button-1>", self._handle_canvas_click)
        self.title_bar.bind("<ButtonPress-1>", self._start_drag)
        self.title_bar.bind("<B1-Motion>", self._drag)
        self.title_label.bind("<ButtonPress-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._drag)
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

        self._drag_x = 0
        self._drag_y = 0

    def _draw_circle_button(self, x: int, y: int, r: int, label: str, fill: str) -> tuple[int, int]:
        circle_id = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="")
        text_id = self.canvas.create_text(
            x,
            y,
            text=label,
            fill="#ffffff",
            font=("Segoe UI", 9, "bold"),
        )
        return circle_id, text_id

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag(self, event: tk.Event) -> None:
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")

    def _handle_canvas_click(self, event: tk.Event) -> None:
        hit = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if self.capture_circle[0] in hit or self.capture_circle[1] in hit:
            self.capture_action()
            return
        if self.copy_circle[0] in hit or self.copy_circle[1] in hit:
            self.copy_action()

    def capture_action(self) -> None:
        if self.is_busy:
            return
        self.is_busy = True
        self.status_var.set("Capturing...")
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self) -> None:
        try:
            self.root.after(0, self.root.withdraw)
            time.sleep(0.2)
            text = run_ocr()
            self.last_text = text
            self.root.after(0, self._set_output_text, text)
            self.root.after(0, lambda: self.status_var.set("OCR complete"))
        except Exception as exc:
            self.root.after(0, lambda: self.status_var.set("Error"))
            self.root.after(0, lambda: messagebox.showerror("OCR Failed", str(exc)))
        finally:
            self.root.after(0, self.root.deiconify)
            self.root.after(0, lambda: setattr(self, "is_busy", False))

    def copy_action(self) -> None:
        if not self.last_text.strip():
            self.status_var.set("Nothing to copy")
            return
        pyperclip.copy(self.last_text)
        self.status_var.set("Copied")

    def _set_output_text(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)


def main() -> int:
    load_dotenv()
    root = tk.Tk()
    OcrOverlayApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
