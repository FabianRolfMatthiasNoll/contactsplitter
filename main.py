# main.py

"""Main module to launch the Kontaktsplitter GUI application."""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from infrastructure.title_repository import TitleRepository
from infrastructure.openai_service import OpenAIService
from application.contact_service import ContactService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KontaktsplitterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Kontaktsplitter")

        # Services initialisieren
        title_file = os.path.join(os.path.dirname(__file__), "titles.json")
        self.title_repo = TitleRepository(title_file)
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            self.ai_service = OpenAIService(api_key=api_key)
        except Exception as e:
            logger.error(f"OpenAI Initialisierung fehlgeschlagen: {e}")

        self.contact_service = ContactService(self.title_repo, self.ai_service)
        self.current_contact = None

        self._build_widgets()

    def _build_widgets(self):
        # — Eingabe-Frame —
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        ttk.Label(input_frame, text="Freitext-Anrede:").pack(anchor="w")
        self.input_text = tk.Text(input_frame, height=4, width=60)
        self.input_text.pack(fill=tk.X)
        ttk.Button(input_frame, text="Zerlegen", command=self._parse_and_update).pack(
            pady=5
        )

        # — Vorschau der Felder —
        output_frame = ttk.LabelFrame(self.root, text="Erkannte Felder")
        output_frame.pack(padx=10, pady=5, fill=tk.X)
        fields = [
            ("Anrede", "anrede"),
            ("Titel", "titel"),
            ("Vorname", "vorname"),
            ("Nachname", "nachname"),
            ("Geschlecht", "geschlecht"),
            ("Sprache", "sprache"),
            ("Briefanrede", "briefanrede"),
        ]
        self.value_vars = {}
        self.value_labels = {}
        for label, field in fields:
            frm = ttk.Frame(output_frame)
            frm.pack(anchor="w", fill=tk.X, padx=5, pady=1)
            ttk.Label(frm, text=f"{label}:").pack(side=tk.LEFT)
            var = tk.StringVar()
            lbl = ttk.Label(frm, textvariable=var)
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.value_vars[field] = var
            self.value_labels[field] = lbl
        self.normal_bg = self.value_labels["anrede"].cget("background")

        # — Unterer Bereich: Speichern, Bearbeiten, Verlauf —
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 1) Speicher-Button
        self.save_btn = ttk.Button(bottom, text="Speichern", command=self._save_current)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 2) Bearbeiten-Button (nur aktueller Kontakt)
        self.edit_btn = ttk.Button(
            bottom, text="Felder bearbeiten", command=self._open_edit_current
        )
        self.edit_btn.pack(side=tk.LEFT)

        # 3) Verlauf als Tabelle
        hist_frame = ttk.Frame(bottom)
        hist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ttk.Label(hist_frame, text="Verlauf:").pack(anchor="w")

        cols = [
            "anrede",
            "titel",
            "vorname",
            "nachname",
            "geschlecht",
            "sprache",
            "briefanrede",
        ]
        self.history_table = ttk.Treeview(
            hist_frame,
            columns=cols,
            show="headings",
            height=6,
        )
        for col in cols:
            self.history_table.heading(col, text=col.capitalize())
            self.history_table.column(col, width=100, anchor="center")
        self.history_table.pack(fill=tk.BOTH, expand=True)

        self._refresh_history_list()

    def _parse_and_update(self):
        text = self.input_text.get("1.0", "end").strip()
        contact = self.contact_service.process_input(text)
        self.current_contact = contact
        self._update_preview(contact)

    def _save_current(self):
        if not self.current_contact:
            messagebox.showwarning("Kein Kontakt", "Bitte zuerst zerlegen.")
            return

        # In-Memory speichern
        self.contact_service.add_to_history(self.current_contact)
        self._refresh_history_list()

        # Alle Felder zurücksetzen
        self.input_text.delete("1.0", "end")
        for var in self.value_vars.values():
            var.set("")
        for lbl in self.value_labels.values():
            lbl.configure(background=self.normal_bg)

        self.current_contact = None
        messagebox.showinfo("Gespeichert", "Kontakt wurde gespeichert.")

    def _refresh_history_list(self):
        # Tabelle leeren
        for iid in self.history_table.get_children():
            self.history_table.delete(iid)
        # Neue Einträge hinzufügen
        for c in self.contact_service.history:
            self.history_table.insert(
                "",
                tk.END,
                values=(
                    c.anrede,
                    c.titel,
                    c.vorname,
                    c.nachname,
                    c.geschlecht,
                    c.sprache,
                    c.briefanrede,
                ),
            )

    def _update_preview(self, contact):
        for field, var in self.value_vars.items():
            var.set(getattr(contact, field))
        for lbl in self.value_labels.values():
            lbl.configure(
                background=(
                    "yellow"
                    if getattr(contact, "needs_review", False)
                    else self.normal_bg
                )
            )

    def _open_edit_current(self):
        if not self.current_contact:
            messagebox.showwarning("Kein Kontakt", "Bitte zuerst zerlegen.")
            return
        self._open_edit_dialog(self.current_contact)

    def _open_edit_dialog(self, contact):
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Kontakt bearbeiten")
        self.edit_window.geometry("600x400")
        self.edit_window.resizable(True, True)

        self.edit_entries: dict[str, tk.StringVar] = {}
        fields = [
            ("Anrede", "anrede"),
            ("Titel", "titel"),
            ("Vorname", "vorname"),
            ("Nachname", "nachname"),
            ("Geschlecht", "geschlecht"),
            ("Sprache", "sprache"),
            ("Briefanrede", "briefanrede"),
        ]
        for idx, (label, field) in enumerate(fields):
            ttk.Label(self.edit_window, text=label).grid(
                row=idx, column=0, sticky="e", padx=5, pady=2
            )
            var = tk.StringVar(value=getattr(contact, field))
            if field == "geschlecht":
                entry = ttk.Combobox(
                    self.edit_window,
                    textvariable=var,
                    values=["m", "w", "-"],
                    state="readonly",
                    width=50,
                )
            else:
                entry = ttk.Entry(self.edit_window, textvariable=var, width=50)
            entry.grid(row=idx, column=1, sticky="we", padx=5, pady=2)
            self.edit_entries[field] = var

        # FIX: Nach Erzeugung die Vorschau updaten
        ttk.Button(
            self.edit_window,
            text="Briefanrede generieren",
            command=lambda: self._regenerate_briefanrede_in_dialog(contact),
        ).grid(row=len(fields), column=0, pady=10)

        ttk.Button(
            self.edit_window,
            text="OK",
            command=lambda: self._close_edit_dialog(contact),
        ).grid(row=len(fields), column=1, pady=10, sticky="e")

    def _regenerate_briefanrede_in_dialog(self, contact):
        """
        Regeneriert via AI die Briefanrede, aktualisiert den Dialog-Eintrag
        und die Vorschau im Hauptfenster.
        """
        self.contact_service.regenerate_briefanrede(contact)
        # Dialog-Entry updaten
        self.edit_entries["briefanrede"].set(contact.briefanrede)
        # Haupt-Vorschau updaten
        self._update_preview(contact)

    def _close_edit_dialog(self, contact):
        # Änderungen zurückschreiben
        for field, var in self.edit_entries.items():
            setattr(contact, field, var.get())

        # Vorschau aktualisieren
        self._update_preview(contact)
        self.edit_window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KontaktsplitterApp(root)
    root.mainloop()
