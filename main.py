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
            logger.error(f"OpenAI initialisierung fehlgeschlagen: {e}")
            # Dummy-Service für lokale Tests
            self.ai_service = type(
                "DummyAI",
                (),
                {
                    "detect_gender": lambda self, n: "-",
                    "detect_language": lambda self, t: "",
                    "generate_briefanrede": lambda self, c: "Sehr geehrte Damen und Herren",
                },
            )()

        self.contact_service = ContactService(self.title_repo, self.ai_service)
        # UI aufbauen
        self._build_widgets()

    def _build_widgets(self):
        # Eingabe-Frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(input_frame, text="Freitext-Anrede:").pack(anchor="w")
        self.input_text = tk.Text(input_frame, height=2, width=50)
        self.input_text.pack(fill=tk.X)

        # Neuer Button zum Parsen
        parse_btn = ttk.Button(
            input_frame, text="Zerlegen", command=self._parse_and_update
        )
        parse_btn.pack(pady=5)

        # Output-Preview
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
            self.value_vars[field] = var
            lbl = ttk.Label(frm, textvariable=var)
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.value_labels[field] = lbl
        self.normal_bg = self.value_labels["anrede"].cget("background")

        # Edit-Button & Verlauf
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Button(
            bottom, text="Felder bearbeiten", command=self._open_edit_current
        ).pack(side=tk.LEFT)
        hist_frame = ttk.Frame(bottom)
        hist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ttk.Label(hist_frame, text="Verlauf:").pack(anchor="w")
        self.history_listbox = tk.Listbox(hist_frame, height=5)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<Double-Button-1>", self._on_history_double_click)

    def _on_input_change(self, event=None):
        # Delay parsing to avoid excessive calls while typing
        if self.parse_after_id:
            self.root.after_cancel(self.parse_after_id)
        self.parse_after_id = self.root.after(500, self._parse_and_update)

    def _parse_and_update(self):
        """
        Wird nur per Klick auf 'Zerlegen' ausgelöst.
        Führt Parsing, KI-Detection und Briefanrede-Generierung aus.
        """
        text = self.input_text.get("1.0", "end").strip()
        contact = self.contact_service.process_input(text)
        self._update_preview(contact)
        # Verlauf aktualisieren
        if self.contact_service.history:
            idx = len(self.contact_service.history) - 1
            name = self._format_contact_name(self.contact_service.history[idx])
            if self.history_listbox.size() >= self.contact_service.history_size:
                self.history_listbox.delete(0)
            self.history_listbox.insert(tk.END, name)

    def _update_preview(self, contact):
        for field, var in self.value_vars.items():
            var.set(getattr(contact, field))
        bg = "yellow" if contact.needs_review else self.normal_bg
        for lbl in self.value_labels.values():
            lbl.configure(background=bg)

    def _format_contact_name(self, contact):
        parts = [
            p
            for p in (contact.anrede, contact.titel, contact.vorname, contact.nachname)
            if p
        ]
        return " ".join(parts) or "(leer)"

    def _open_edit_current(self):
        if not self.contact_service.history:
            return
        self._open_edit_dialog(
            self.contact_service.history[-1], len(self.contact_service.history) - 1
        )

    def _on_history_double_click(self, event=None):
        sel = self.history_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._open_edit_dialog(self.contact_service.history[idx], idx)

    def _open_edit_dialog(self, contact, history_index):
        # Create a modal edit dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Felder bearbeiten")
        dialog.grab_set()  # make this window modal
        # Fields in dialog
        fields = [
            ("Anrede", "anrede"),
            ("Titel", "titel"),
            ("Vorname", "vorname"),
            ("Nachname", "nachname"),
            ("Geschlecht", "geschlecht"),
            ("Sprache", "sprache"),
            ("Briefanrede", "briefanrede"),
        ]
        entries = {}
        gender_var = tk.StringVar(value=contact.geschlecht)
        lang_var = tk.StringVar(value=contact.sprache if contact.sprache else "-")
        for label_text, field in fields:
            frm = ttk.Frame(dialog)
            frm.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frm, text=f"{label_text}:").pack(side=tk.LEFT)
            if field == "geschlecht":
                # Dropdown for gender
                gender_options = ["m", "w", "-"]
                gender_menu = ttk.OptionMenu(
                    frm, gender_var, contact.geschlecht or "-", *gender_options
                )
                gender_menu.pack(side=tk.LEFT)
                entries[field] = gender_menu
            elif field == "sprache":
                lang_options = ["de", "en", "fr", "it", "es", "-"]
                lang_menu = ttk.OptionMenu(
                    frm,
                    lang_var,
                    contact.sprache if contact.sprache else "-",
                    *lang_options,
                )
                lang_menu.pack(side=tk.LEFT)
                entries[field] = lang_menu
            elif field == "briefanrede":
                # Briefanrede as read-only Entry
                brief_entry = ttk.Entry(frm, width=50)
                brief_entry.insert(0, contact.briefanrede)
                brief_entry.configure(state="readonly")
                brief_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = brief_entry
            else:
                e = ttk.Entry(frm, width=30)
                e.insert(0, getattr(contact, field))
                e.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries[field] = e
        # Buttons in dialog
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=5)
        regen_btn = ttk.Button(
            btn_frame,
            text="Briefanrede neu erzeugen",
            command=lambda: self._regenerate_briefanrede_in_dialog(
                contact, entries, gender_var, lang_var
            ),
        )
        regen_btn.pack(side=tk.LEFT, padx=5)
        save_title_btn = ttk.Button(
            btn_frame,
            text="Titel speichern",
            command=lambda: self._save_titles_from_dialog(entries["titel"].get()),
        )
        save_title_btn.pack(side=tk.LEFT, padx=5)
        close_btn = ttk.Button(
            btn_frame,
            text="Schließen",
            command=lambda: self._close_edit_dialog(
                dialog, contact, entries, gender_var, lang_var, history_index
            ),
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _regenerate_briefanrede_in_dialog(self, contact, entries, gender_var, lang_var):
        # Update contact object from entries (except briefanrede which is output)
        contact.anrede = entries["anrede"].get().strip()
        contact.titel = entries["titel"].get().strip()
        contact.vorname = entries["vorname"].get().strip()
        contact.nachname = entries["nachname"].get().strip()
        contact.geschlecht = gender_var.get() if gender_var.get() else "-"
        contact.sprache = lang_var.get() if lang_var.get() != "-" else ""
        # Regenerate briefanrede
        self.contact_service.regenerate_briefanrede(contact)
        # Update the briefanrede entry in dialog
        brief_entry = entries["briefanrede"]
        brief_entry.configure(state="normal")
        brief_entry.delete(0, tk.END)
        brief_entry.insert(0, contact.briefanrede)
        brief_entry.configure(state="readonly")

    def _save_titles_from_dialog(self, title_text):
        # Save each title in the given text to repository
        titles = title_text.split()
        added_any = False
        for t in titles:
            if self.contact_service.save_new_title(t):
                added_any = True
        if added_any:
            messagebox.showinfo(
                "Titel gespeichert", "Neue Titel wurden zur Titelliste hinzugefügt."
            )
        else:
            messagebox.showinfo(
                "Titel gespeichert",
                "Keine neuen Titel zum Speichern (bereits bekannt).",
            )

    def _close_edit_dialog(
        self, dialog, contact, entries, gender_var, lang_var, history_index
    ):
        # Update contact object with final changes
        contact.anrede = entries["anrede"].get().strip()
        contact.titel = entries["titel"].get().strip()
        contact.vorname = entries["vorname"].get().strip()
        contact.nachname = entries["nachname"].get().strip()
        contact.geschlecht = gender_var.get() if gender_var.get() else "-"
        contact.sprache = lang_var.get() if lang_var.get() != "-" else ""
        # Ensure briefanrede is up-to-date (regenerate in case user didn't click regen)
        self.contact_service.regenerate_briefanrede(contact)
        # Update main preview if this contact is the current one
        if history_index == len(self.contact_service.history) - 1:
            self._update_preview(contact)
        # Update history list entry text
        self.history_listbox.delete(history_index)
        self.history_listbox.insert(history_index, self._format_contact_name(contact))
        # Close the dialog window
        dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KontaktsplitterApp(root)
    root.mainloop()
