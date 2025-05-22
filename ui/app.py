import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox, Style
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
        self._item_to_contact: Dict[str, Contact] = {}
        self.field_entries: Dict[str, ttk.Entry] = {}

        # Styles für Fehler-Highlight
        self.style = Style(self.root)
        self.style.configure("Error.TEntry", fieldbackground="IndianRed1")
        self.style.configure("Error.TCombobox", fieldbackground="IndianRed1")

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
        frm.columnconfigure(1, weight=1)

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
            ttk.Label(frm, text=f"{label_text}:").grid(
                row=i, column=0, sticky="w", pady=2
            )
            var = tk.StringVar()
            if field_name == "geschlecht":
                entry = Combobox(
                    frm,
                    textvariable=var,
                    values=["-", "m", "w"],
                    width=37,
                    state="readonly",
                    style="TCombobox",
                )
            else:
                entry = ttk.Entry(frm, textvariable=var, width=40, style="TEntry")
            entry.grid(row=i, column=1, columnspan=2, sticky="we", pady=2)

            self.field_vars[field_name] = var
            self.field_entries[field_name] = entry

        # Aktions-Buttons
        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=9, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frm, text="Speichern", command=self._on_save).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(btn_frm, text="Anrede neu", command=self._on_regenerate).grid(
            row=0, column=1, padx=5
        )

        # Kontaktbuch (Treeview)
        hist_frm = ttk.LabelFrame(self.root, text="Kontaktbuch", padding=5)
        hist_frm.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

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
            self.tree.heading(
                col,
                text=col.capitalize(),
                command=lambda _col=col: self._sort_by(_col, False),
            )
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(hist_frm, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        hist_frm.columnconfigure(0, weight=1)
        hist_frm.rowconfigure(0, weight=1)

    def _on_parse(self):
        raw = self.raw_input.get().strip()
        if not raw:
            messagebox.showwarning("Eingabe fehlt", "Bitte Rohdaten eingeben.")
            return
        try:
            contact = self.service.process(raw)
            self.current_contact = contact
            self._populate_fields(contact)

            # Unstimmigkeiten melden & markieren
            if contact.review_fields:
                msgs = "\n".join(f"- {f}" for f in contact.review_fields)
                messagebox.showwarning(
                    "Unstimmigkeiten erkannt",
                    f"In folgenden Feldern sind Probleme:\n{msgs}",
                )
                for fname in self.field_entries:
                    if fname in contact.review_fields:
                        self._highlight_field(fname)
                    else:
                        self._reset_field(fname)
        except Exception as e:
            messagebox.showerror("Fehler beim Parsen", str(e))

    def _populate_fields(self, contact: Contact):
        for field, var in self.field_vars.items():
            var.set(getattr(contact, field, ""))

    def _on_save(self):
        if not self.current_contact:
            messagebox.showwarning("Nichts zu speichern", "Kein Kontakt vorhanden.")
            return
        # Benutzeränderungen übernehmen
        for field, var in self.field_vars.items():
            setattr(self.current_contact, field, var.get().strip())
        try:
            self.service.save_contact(self.current_contact)
            self._refresh_history()
            messagebox.showinfo("Gespeichert", "Kontakt gespeichert.")

            # Felder leeren und Highlight zurücksetzen
            self.raw_input.delete(0, tk.END)
            for fname in self.field_entries:
                self.field_vars[fname].set("")
                self._reset_field(fname)
            self.current_contact = None
            for sel in self.tree.selection():
                self.tree.selection_remove(sel)
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

    def _on_regenerate(self):
        if not self.current_contact:
            messagebox.showwarning("Keine Anrede", "Kein Kontakt ausgewählt.")
            return
        # Aktualisierte Werte übernehmen
        for field, var in self.field_vars.items():
            setattr(self.current_contact, field, var.get().strip())
        try:
            self.service.regenerate_briefanrede(self.current_contact)
            self.field_vars["briefanrede"].set(self.current_contact.briefanrede)
            self._refresh_history()
        except Exception as e:
            messagebox.showerror("Fehler bei Anrede", str(e))

    def _highlight_field(self, field_name: str):
        widget = self.field_entries[field_name]
        if isinstance(widget, Combobox):
            widget.configure(style="Error.TCombobox")
        else:
            widget.configure(style="Error.TEntry")

    def _reset_field(self, field_name: str):
        widget = self.field_entries[field_name]
        if isinstance(widget, Combobox):
            widget.configure(style="TCombobox")
        else:
            widget.configure(style="TEntry")

    def _refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._item_to_contact.clear()
        for contact in self.service.get_history():
            vals = tuple(
                getattr(contact, col)
                for col in (
                    "anrede",
                    "titel",
                    "vorname",
                    "nachname",
                    "geschlecht",
                    "sprache",
                    "briefanrede",
                )
            )
            item = self.tree.insert("", "end", values=vals)
            self._item_to_contact[item] = contact

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        contact = self._item_to_contact.get(sel[0])
        if contact:
            self.current_contact = contact
            self._populate_fields(contact)

    def _sort_by(self, col: str, descending: bool):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: t[0].lower(), reverse=descending)
        except Exception:
            data.sort(reverse=descending)
        for idx, (_, k) in enumerate(data):
            self.tree.move(k, "", idx)
        self.tree.heading(col, command=lambda: self._sort_by(col, not descending))

    def _open_title_manager(self):
        dialog = TitleManagerDialog(self.root, self.title_repo)
        self.root.wait_window(dialog.top)
