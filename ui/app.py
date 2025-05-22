import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from domain.contact import Contact
from ui.title_manager import TitleManagerDialog
from application.interfaces import IContactService, ITitleRepository


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
        # Map Treeview item IDs to Contact instances
        self._item_to_contact: Dict[str, Contact] = {}

        self._build_menu()
        self._build_widgets()
        self._refresh_history()

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        menu_tools = tk.Menu(menubar, tearoff=0)
        menu_tools.add_command(
            label="Titel verwalten…", command=self._open_title_manager
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
            ttk.Label(frm, text=label_text + ":").grid(
                row=i, column=0, sticky="w", pady=2
            )
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

        # Kontaktbuch (History) als Treeview
        hist_frm = ttk.LabelFrame(self.root, text="Kontaktbuch", padding=5)
        hist_frm.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        columns = (
            "anrede",
            "titel",
            "vorname",
            "nachname",
            "geschlecht",
            "sprache",
            "briefanrede",
        )
        self.tree = ttk.Treeview(hist_frm, columns=columns, show="headings")
        for col in columns:
            # Spalten-Header klickbar zum Sortieren
            self.tree.heading(
                col,
                text=col.capitalize(),
                command=lambda _col=col: self._sort_by(_col, False),
            )
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(hist_frm, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

    def _on_parse(self):
        raw = self.raw_input.get().strip()
        if not raw:
            messagebox.showwarning(
                "Eingabe fehlt", "Bitte geben Sie zuerst Rohdaten ein."
            )
            return
        try:
            contact = self.service.process(raw)
            self.current_contact = contact
            self._populate_fields(contact)
        except Exception as e:
            messagebox.showerror("Fehler beim Parsen", str(e))

    def _populate_fields(self, contact: Contact):
        for field, var in self.field_vars.items():
            var.set(getattr(contact, field, ""))

        self.inacc_text.config(state="normal")
        self.inacc_text.delete("1.0", tk.END)
        for inc in contact.inaccuracies:
            self.inacc_text.insert(tk.END, f"- {inc}\n")
        self.inacc_text.config(state="disabled")

    def _on_save(self):
        if not self.current_contact:
            messagebox.showwarning(
                "Nichts zu speichern", "Kein Kontakt zum Speichern vorhanden."
            )
            return
        try:
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
            # Aktualisiere auch den Eintrag im Treeview
            self._refresh_history()
        except Exception as e:
            messagebox.showerror("Fehler bei Anrede", str(e))

    def _refresh_history(self):
        # Tree leeren
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_to_contact.clear()

        # Neu befüllen
        for contact in self.service.get_history():
            vals = (
                contact.anrede,
                contact.titel,
                contact.vorname,
                contact.nachname,
                contact.geschlecht,
                contact.sprache,
                contact.briefanrede,
            )
            item_id = self.tree.insert("", "end", values=vals)
            self._item_to_contact[item_id] = contact

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        contact = self._item_to_contact.get(item_id)
        if contact:
            self.current_contact = contact
            self._populate_fields(contact)

    def _sort_by(self, col: str, descending: bool):
        # Daten abrufen und sortieren
        data = [
            (self.tree.set(child, col), child) for child in self.tree.get_children("")
        ]
        try:
            data.sort(key=lambda t: t[0].lower(), reverse=descending)
        except Exception:
            data.sort(reverse=descending)

        # Reihenfolge im Treeview aktualisieren
        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)

        # Toggle für nächste Sortierung
        self.tree.heading(col, command=lambda: self._sort_by(col, not descending))

    def _open_title_manager(self):
        try:
            dialog = TitleManagerDialog(self.root, self.title_repo)
            self.root.wait_window(dialog.top)
        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Titel-Manager konnte nicht geöffnet werden:\n{e}"
            )
