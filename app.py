"""
Smart Web Scraper — GUI Application
Built with Tkinter | Clean & Professional
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.core import SmartScraper
from exporters.export import Exporter


class SmartScraperApp:
    """Main GUI Application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Smart Web Scraper")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.scraper = None
        self.data = []

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        """Build the complete UI."""
        # ── Header ──
        header = tk.Frame(self.root, bg="#313244", pady=15)
        header.pack(fill="x")
        tk.Label(
            header, text="🚀 Smart Web Scraper",
            font=("Segoe UI", 20, "bold"),
            fg="#cdd6f4", bg="#313244"
        ).pack()
        tk.Label(
            header, text="AI-Powered | Anti-Bot | Multi-Format Export",
            font=("Segoe UI", 10),
            fg="#a6adc8", bg="#313244"
        ).pack()

        # ── Main Content ──
        main = tk.Frame(self.root, bg="#1e1e2e", padx=20, pady=15)
        main.pack(fill="both", expand=True)

        # ── URL Input ──
        self._label(main, "🌐 Target URL")
        url_frame = tk.Frame(main, bg="#1e1e2e")
        url_frame.pack(fill="x", pady=(0, 10))
        self.url_entry = self._entry(url_frame, "https://example.com/products")
        self.url_entry.pack(side="left", fill="x", expand=True)

        # ── Fields ──
        self._label(main, "📋 Fields to Extract (comma separated)")
        self.fields_entry = self._entry(
            main, "title, price, description, image, link, rating"
        )
        self.fields_entry.pack(fill="x", pady=(0, 10))

        # ── Options Row ──
        opts = tk.Frame(main, bg="#1e1e2e")
        opts.pack(fill="x", pady=(0, 15))

        # Max pages
        tk.Label(opts, text="📄 Max Pages:", fg="#cdd6f4",
                 bg="#1e1e2e", font=("Segoe UI", 10)).pack(side="left")
        self.pages_var = tk.StringVar(value="10")
        tk.Spinbox(
            opts, from_=1, to=100, width=5,
            textvariable=self.pages_var,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(5, 20))

        # Delay
        tk.Label(opts, text="⏱ Delay (sec):", fg="#cdd6f4",
                 bg="#1e1e2e", font=("Segoe UI", 10)).pack(side="left")
        self.delay_var = tk.StringVar(value="1.5")
        tk.Spinbox(
            opts, from_=0.5, to=10, increment=0.5, width=5,
            textvariable=self.delay_var,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(5, 20))

        # AI Toggle
        self.ai_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            opts, text="🤖 AI Selector",
            variable=self.ai_var,
            fg="#cdd6f4", bg="#1e1e2e",
            selectcolor="#313244",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 20))

        # ── Buttons ──
        btn_frame = tk.Frame(main, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=(0, 15))

        self.start_btn = self._btn(
            btn_frame, "▶ Start Scraping", "#a6e3a1", self._start_scraping
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        self._btn(btn_frame, "⏹ Stop", "#f38ba8", self._stop).pack(side="left", padx=(0, 10))
        self._btn(btn_frame, "💾 Export CSV", "#89b4fa", self._export_csv).pack(side="left", padx=(0, 10))
        self._btn(btn_frame, "📊 Export Excel", "#a6e3a1", self._export_excel).pack(side="left", padx=(0, 10))
        self._btn(btn_frame, "🗑 Clear", "#6c7086", self._clear).pack(side="left")

        # ── Progress ──
        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 10))

        # ── Status ──
        self.status_var = tk.StringVar(value="Ready — Enter URL and click Start")
        tk.Label(
            main, textvariable=self.status_var,
            fg="#a6adc8", bg="#1e1e2e",
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        # ── Results Table ──
        self._label(main, "📊 Results")
        table_frame = tk.Frame(main, bg="#1e1e2e")
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # ── Footer ──
        footer = tk.Frame(self.root, bg="#313244", pady=8)
        footer.pack(fill="x", side="bottom")
        self.items_label = tk.Label(
            footer, text="Items: 0",
            fg="#a6adc8", bg="#313244",
            font=("Segoe UI", 10)
        )
        self.items_label.pack(side="left", padx=20)

    def _start_scraping(self):
        """Start scraping in background thread."""
        url = self.url_entry.get().strip()
        if not url or not url.startswith("http"):
            messagebox.showerror("Error", "Please enter a valid URL")
            return

        fields = [f.strip() for f in self.fields_entry.get().split(",") if f.strip()]
        if not fields:
            messagebox.showerror("Error", "Please enter at least one field")
            return

        self._set_status("🔄 Scraping...")
        self.progress.start()
        self.start_btn.config(state="disabled")

        def run():
            try:
                self.scraper = SmartScraper(
                    url=url,
                    use_ai=self.ai_var.get(),
                    delay=float(self.delay_var.get())
                )
                self.data = self.scraper.extract_all_pages(
                    fields=fields,
                    max_pages=int(self.pages_var.get())
                )
                self.root.after(0, self._show_results)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"❌ Error: {e}"))
            finally:
                self.root.after(0, self._stop_progress)

        threading.Thread(target=run, daemon=True).start()

    def _show_results(self):
        """Display results in table."""
        if not self.data:
            self._set_status("⚠ No data found")
            return

        # Setup columns
        columns = list(self.data[0].keys())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, minwidth=80)

        # Insert rows
        self.tree.delete(*self.tree.get_children())
        for row in self.data:
            self.tree.insert("", "end", values=list(row.values()))

        self._set_status(f"✅ Done! {len(self.data)} items found")
        self.items_label.config(text=f"Items: {len(self.data)}")

    def _export_csv(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to export")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            Exporter(self.data).to_csv(path)
            messagebox.showinfo("Success", f"Saved to {path}")

    def _export_excel(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to export")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if path:
            Exporter(self.data).to_excel(path)
            messagebox.showinfo("Success", f"Saved to {path}")

    def _stop(self):
        self.scraper = None
        self._stop_progress()
        self._set_status("⏹ Stopped")

    def _clear(self):
        self.tree.delete(*self.tree.get_children())
        self.data = []
        self.items_label.config(text="Items: 0")
        self._set_status("🗑 Cleared")

    def _stop_progress(self):
        self.progress.stop()
        self.start_btn.config(state="normal")

    def _set_status(self, msg: str):
        self.status_var.set(msg)

    def _label(self, parent, text: str):
        tk.Label(
            parent, text=text,
            fg="#89dceb", bg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(8, 2))

    def _entry(self, parent, placeholder: str) -> tk.Entry:
        entry = tk.Entry(
            parent, font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat", bd=8
        )
        entry.insert(0, placeholder)
        return entry

    def _btn(self, parent, text: str, color: str, command) -> tk.Button:
        return tk.Button(
            parent, text=text, command=command,
            bg=color, fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=6,
            cursor="hand2"
        )


if __name__ == "__main__":
    SmartScraperApp()
