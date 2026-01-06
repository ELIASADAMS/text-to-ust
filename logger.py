# logger.py - eli_lab TESTER v2.2 (100% FIXED)
import logging
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
from collections import Counter


class TesterLogger:
    def __init__(self, parent):
        self.parent = parent
        self.gui_logs = []
        self.log_text = None
        self.stats = {
            'phonemes': Counter(),
            'notes': [],
            'durations': [],
            'pauses': 0,
            'sections': 0,
            'errors': 0
        }

    def setup(self):
        """eli_lab tester logging - bulletproof"""
        try:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

            file_handler = logging.FileHandler('eli_lab_tester.log', encoding='utf-8')
            file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s'))

            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            root_logger.handlers.clear()
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)

            gui_handler = logging.Handler()
            gui_handler.setLevel(logging.INFO)
            gui_handler.emit = self._safe_gui_emit

            root_logger.addHandler(gui_handler)
            self._create_eli_lab_gui()

            self.info("🧪 eli_lab TESTER v2.2 ACTIVE - eli_lab_tester.log")
            self.info("🎵 Hiro UST v4.2 Ready | eli_lab crew")

        except Exception as e:
            print(f"Logger setup failed: {e}")

    def info(self, msg):
        logging.info(msg)
        self._add_to_gui("INFO", msg)

    def warning(self, msg):
        logging.warning(msg)
        self._add_to_gui("WARNING", msg)

    def error(self, msg):
        self.stats['errors'] += 1
        logging.error(msg)
        self._add_to_gui("ERROR", f"❌ ERROR #{self.stats['errors']}: {msg}")

    def _add_to_gui(self, level, msg):  # ✅ FIXED - New method
        """Safe GUI logging"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted = f"[{timestamp}] {level:7} | {msg}"
            self.gui_logs.append((formatted, level))
            if self.parent.root.winfo_exists() and self.log_text:
                self.parent.root.after(0, self._update_gui_logs)
        except:
            pass

    def safe_max(self, values, default=0):
        return max(values) if values else default

    def safe_range(self, values):
        return max(values) - min(values) if len(values) >= 2 else 0

    def safe_avg(self, values):
        return sum(values) / len(values) if values else 0

    def log_phonemes(self, phonemes):
        if phonemes:
            self.stats['phonemes'].update(phonemes)
            top = dict(self.stats['phonemes'].most_common(5))
            self.info(f"📊 PHONEMES: {len(phonemes)} | Top: {top}")
        else:
            self.warning("📊 No phonemes detected")

    def log_melody(self, notes, scale):
        if notes:
            self.stats['notes'].extend(notes)
            note_range = self.safe_range(self.stats['notes'])
            self.info(f"🎼 MELODY: {len(notes)} notes | Range: {note_range:.1f} | Scale: {scale}")
        else:
            self.warning("🎼 No melody notes")

    def log_timing(self, durations, pauses):
        if durations:
            self.stats['durations'].extend(durations)
            avg_dur = self.safe_avg(durations)
            self.info(f"⏱️ TIMING: Avg {avg_dur:.0f}ticks | Pauses: {pauses}")
        self.stats['pauses'] += pauses

    def log_sections(self, sections):
        section_count = len(sections) if sections else 0
        self.stats['sections'] += section_count
        section_names = list(sections.keys()) if sections else ['none']
        self.info(f"📂 SECTIONS: {section_count} | {section_names}")

    def show_stats(self):
        """100% crash-proof stats"""
        try:
            phoneme_total = sum(self.stats['phonemes'].values())
            note_count = len(self.stats['notes'])
            note_range = self.safe_range(self.stats['notes'])
            dur_count = len(self.stats['durations'])
            dur_avg = self.safe_avg(self.stats['durations'])

            stats_msg = f"""🧪 eli_lab TEST STATS v2.2:
📊 Phonemes: {phoneme_total} | {dict(self.stats['phonemes'].most_common(6))}
🎼 Notes: {note_count} | Range: {note_range:.1f}
⏱️ Durations: {dur_count} | Avg: {dur_avg:.0f}ticks
📂 Pauses: {self.stats['pauses']} | Sections: {self.stats['sections']}
❌ Errors: {self.stats['errors']}"""

            self.info(stats_msg)
        except Exception as e:
            self.error(f"Stats calculation failed: {e}")

    def _safe_gui_emit(self, record):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            level = record.levelname
            msg = record.getMessage()
            formatted = f"[{timestamp}] {level:7} | {msg}"
            self.gui_logs.append((formatted, level))
            if self.parent.root.winfo_exists() and self.log_text:
                self.parent.root.after(0, self._update_gui_logs)
        except:
            pass

    def _create_eli_lab_gui(self):
        self.log_frame = ttk.LabelFrame(self.parent.root, text="🧪 eli_lab TESTER", padding=8)
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        btn_frame = ttk.Frame(self.log_frame)
        btn_frame.pack(fill="x", pady=(0, 8))
        ttk.Button(btn_frame, text="📊 STATS", command=self.show_stats).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🧹 CLEAR", command=self.clear).pack(side="right", padx=2)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, height=8, state="disabled",
            font=("Consolas", 9), bg='#1a1a1a', fg='#e8e8e8',
            insertbackground='#ffffff'
        )
        self.log_text.pack(fill="both", expand=True)

        self.log_text.tag_config("INFO", foreground="#4CAF50")
        self.log_text.tag_config("WARNING", foreground="#FF9800")
        self.log_text.tag_config("ERROR", foreground="#F44336")

        scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _update_gui_logs(self):
        if not self.log_text: return
        try:
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            for msg, level in self.gui_logs[-100:]:
                self.log_text.insert("end", msg + "\n", level)
            self.log_text.config(state="disabled")
            self.log_text.see("end")
        except:
            pass

    def clear(self):
        self.gui_logs.clear()
        self.stats = {'phonemes': Counter(), 'notes': [], 'durations': [], 'pauses': 0, 'sections': 0, 'errors': 0}
        self._update_gui_logs()
        self.info("🧹 eli_lab stats cleared - Ready!")
