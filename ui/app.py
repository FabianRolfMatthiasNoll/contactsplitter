# ui/kontaktsplitter_app.py

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from domain.contact import Contact
from ui.title_manager import TitleManagerDialog
from application.interfaces import IContactService
from application.interfaces import ITitleRepository

class KontaktsplitterApp:
    def __init__(
        self,
        root: tk.Tk,
        contact_service: IContactService,
        title_repo: ITitleRepository,
    ):
        self.root = root
        self.service = contact_service
        self.title_repo = title_repo
        self.current_contact: Contact = None

        self._build_menu()
        self._build_widgets()
        self._refresh_history()

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        # Titel-Manager
        menu_tools = tk.Menu(menubar, tearoff=0)
        menu_tools.add_command(
            label="Titel verwalten…",
            command=self._open_title_manager
        )
        menubar.add_cascade(label="Extras", menu=menu_tools)
        self.root.config(menu=menubar)

    def _build_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Eingabe-Rohdaten
        ttk.Label(frm, text="Rohdaten:").grid(row=0, column=0, sticky="w")
        self.raw_input = ttk.Entry(frm, width=40)
        self.raw_input.grid(row=0, column=1, columnspan=2, sticky="we")
        ttk.Button(frm, text="Parsen", command=self._on_parse).grid(
            row=0, column=3, padx=5
        )

        # Ergebnis-Felder
        labels = [
            ("Anrede", "anrede"),
            ("Titel", "titel"),
            ("Vorname", "vorname"),
            ("Nachname", "nachname"),
            ("Geschlecht", "geschlecht"),
            ("Sprache", "sprache"),
            ("Briefanrede", "briefanrede"),
        ]
        self.field_vars: Dict[str, tk.StringVar] = {}
        for i, (label_text, field_name) in enumerate(labels, start=1):
            ttk.Label(frm, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(frm, textvariable=var, width=40)
            entry.grid(row=i, column=1, columnspan=2, sticky="we", pady=2)
            self.field_vars[field_name] = var

        # Ungenauigkeiten / Review-Felder
        ttk.Label(frm, text="Inaccuracies:").grid(row=8, column=0, sticky="nw", pady=2)
        self.inacc_text = tk.Text(frm, width=40, height=4, state="disabled")
        self.inacc_text.grid(row=8, column=1, columnspan=2, sticky="we", pady=2)

        # Aktions-Buttons
        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=9, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frm, text="Speichern", command=self._on_save).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frm, text="Anrede neu", command=self._on_regenerate).grid(
            row=0, column=1, padx=5
        )

        # Historie
        hist_frm = ttk.LabelFrame(self.root, text="Historie", padding=5)
        hist_frm.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.hist_list = tk.Listbox(hist_frm, height=15, width=30)
        self.hist_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(hist_frm, orient="vertical", command=self.hist_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.hist_list.config(yscrollcommand=scrollbar.set)
        self.hist_list.bind("<<ListboxSelect>>", self._on_history_select)

        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _on_parse(self):
        raw = self.raw_input.get().strip()
        if not raw:
            messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie zuerst Rohdaten ein.")
            return
        try:
            contact = self.service.process(raw)
            self.current_contact = contact
            self._populate_fields(contact)
        except Exception as e:
            messagebox.showerror("Fehler beim Parsen", str(e))

    def _populate_fields(self, contact: Contact):
        # Einträge auffüllen
        for field, var in self.field_vars.items():
            var.set(getattr(contact, field, ""))

        # Inaccuracies anzeigen
        self.inacc_text.config(state="normal")
        self.inacc_text.delete("1.0", tk.END)
        for inc in contact.inaccuracies:
            self.inacc_text.insert(tk.END, f"- {inc}\n")
        self.inacc_text.config(state="disabled")

    def _on_save(self):
        if not self.current_contact:
            messagebox.showwarning("Nichts zu speichern", "Kein Kontakt zum Speichern vorhanden.")
            return
        try:
            # Felder zurücklesen (evtl. manuelle Korrektur)
            for field, var in self.field_vars.items():
                setattr(self.current_contact, field, var.get().strip())
            self.service.save_contact(self.current_contact)
            self._refresh_history()
            messagebox.showinfo("Gespeichert", "Kontakt erfolgreich gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

    def _on_regenerate(self):
        if not self.current_contact:
            messagebox.showwarning("Keine Anrede", "Kein Kontakt ausgewählt.")
            return
        try:
            self.service.regenerate_briefanrede(self.current_contact)
            self.field_vars["briefanrede"].set(self.current_contact.briefanrede)
        except Exception as e:
            messagebox.showerror("Fehler bei Anrede", str(e))

    def _refresh_history(self):
        self.hist_list.delete(0, tk.END)
        for idx, contact in enumerate(self.service.get_history()):
            display = f"{idx+1}: {contact.vorname} {contact.nachname}"
            self.hist_list.insert(tk.END, display)

    def _on_history_select(self, event):
        sel = self.hist_list.curselection()
        if not sel:
            return
        idx = sel[0]
        contact = self.service.get_history()[idx]
        self.current_contact = contact
        self._populate_fields(contact)

    def _open_title_manager(self):
        try:
            dialog = TitleManagerDialog(self.root, self.title_repo)
            self.root.wait_window(dialog.top)
        except Exception as e:
            messagebox.showerror("Fehler", f"Titel-Manager konnte nicht geöffnet werden:\n{e}")
