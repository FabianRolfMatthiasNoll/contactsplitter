import re
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
        self.unsaved_changes = False

        # Styles für Fehler-Highlight
        self.style = Style(self.root)
        self.style.configure("Error.TEntry", fieldbackground="IndianRed1")
        self.style.configure("Error.TCombobox", fieldbackground="IndianRed1")

        self._build_menu()
        self._build_widgets()
        self._bind_field_traces()
        self._refresh_history()
        self._set_buttons_state(parsed=False)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Titel verwalten…", command=self._open_title_manager)
        menubar.add_cascade(label="Extras", menu=tools)
        self.root.config(menu=menubar)

    def _build_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")
        frm.columnconfigure(1, weight=1)

        # Rohdaten
        ttk.Label(frm, text="Rohdaten:").grid(row=0, column=0, sticky="w")
        self.raw_input = ttk.Entry(frm, width=40)
        self.raw_input.grid(row=0, column=1, columnspan=2, sticky="we")
        self.parse_button = ttk.Button(frm, text="Parsen", command=self._on_parse)
        self.parse_button.grid(row=0, column=3, padx=5)

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
        for i, (lbl, name) in enumerate(labels, start=1):
            ttk.Label(frm, text=f"{lbl}:").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            if name == "geschlecht":
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
            self.field_vars[name] = var
            self.field_entries[name] = entry

        # Buttons
        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=9, column=0, columnspan=4, pady=10)
        self.save_button = ttk.Button(btn_frm, text="Speichern", command=self._on_save)
        self.save_button.grid(row=0, column=0, padx=5)
        self.regen_button = ttk.Button(
            btn_frm, text="Anrede neu", command=self._on_regenerate
        )
        self.regen_button.grid(row=0, column=1, padx=5)

        # Statuszeile
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", anchor="w"
        )
        status.grid(row=1, column=0, columnspan=2, sticky="we")

        # Kontaktbuch
        hist_frm = ttk.LabelFrame(self.root, text="Kontaktbuch", padding=5)
        hist_frm.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        cols = (
            "anrede",
            "titel",
            "vorname",
            "nachname",
            "geschlecht",
            "sprache",
            "briefanrede",
        )
        self.tree = ttk.Treeview(hist_frm, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(
                c, text=c.capitalize(), command=lambda _c=c: self._sort_by(_c, False)
            )
            self.tree.column(c, width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(hist_frm, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        hist_frm.columnconfigure(0, weight=1)
        hist_frm.rowconfigure(0, weight=1)

    def _bind_field_traces(self):
        for var in self.field_vars.values():
            var.trace_add("write", self._on_field_change)

    def _on_field_change(self, *args):
        if self.current_contact:
            self.unsaved_changes = True
            self.save_button.config(state="normal")

    def _validate_raw(self, raw: str) -> bool:
        for ch in raw:
            if not (ch.isalpha() or ch in (" ", "-", ".", ",")):
                messagebox.showerror(
                    "Ungültiges Zeichen", f"Zeichen „{ch}“ nicht erlaubt."
                )
                return False
        return True

    def _on_parse(self):
        if self.unsaved_changes:
            cont = messagebox.askyesno(
                "Ungespeicherte Änderungen",
                "Ungespeicherte manuelle Änderungen gehen verloren. Fortfahren?",
            )
            if not cont:
                return
            self.unsaved_changes = False

        raw = self.raw_input.get().strip()
        if not raw:
            messagebox.showwarning("Eingabe fehlt", "Bitte einen Namen eingeben.")
            return
        if not self._validate_raw(raw):
            return

        # Busy
        self._set_busy(True, "Parsen…")
        try:
            contact = self.service.process(raw)
            self.current_contact = contact
            self._populate_fields(contact)
            self._set_buttons_state(parsed=True)
        except Exception as e:
            messagebox.showerror("Fehler beim Parsen", str(e))
        finally:
            self._set_busy(False)

    def _populate_fields(self, contact: Contact):
        for f, var in self.field_vars.items():
            var.set(getattr(contact, f, ""))

    def _on_save(self):
        if not self.current_contact:
            return
        # Übernehmen
        for f, var in self.field_vars.items():
            setattr(self.current_contact, f, var.get().strip())
        try:
            self.service.save_contact(self.current_contact)
            self._refresh_history()
            messagebox.showinfo("Gespeichert", "Kontakt gespeichert.")
            # Reset
            self.raw_input.delete(0, tk.END)
            for f in self.field_vars:
                self.field_vars[f].set("")
            self.current_contact = None
            self.unsaved_changes = False
            self._set_buttons_state(parsed=False)
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

    def _on_regenerate(self):
        if not self.current_contact:
            return
        # Übernehmen
        for f, var in self.field_vars.items():
            setattr(self.current_contact, f, var.get().strip())
        # Busy
        self._set_busy(True, "Erzeuge Anrede…")
        try:
            self.service.regenerate_briefanrede(self.current_contact)
            self.field_vars["briefanrede"].set(self.current_contact.briefanrede)
            self._refresh_history()
        except Exception as e:
            messagebox.showerror("Fehler bei Anrede", str(e))
        finally:
            self._set_busy(False)

    def _set_busy(self, busy: bool, msg: str = ""):
        state = "disabled" if busy else "normal"
        self.parse_button.config(state=state)
        self.save_button.config(state=state if not busy else "disabled")
        self.regen_button.config(
            state=state if not busy and self.current_contact else "disabled"
        )
        self.status_var.set(msg if busy else "")

    def _set_buttons_state(self, parsed: bool):
        if parsed:
            self.save_button.config(state="normal")
            self.regen_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")
            self.regen_button.config(state="disabled")

    def _refresh_history(self):
        self.tree.delete(*self.tree.get_children())
        self._item_to_contact.clear()
        for c in self.service.get_history():
            vals = tuple(
                getattr(c, col)
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
            iid = self.tree.insert("", "end", values=vals)
            self._item_to_contact[iid] = c

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        c = self._item_to_contact[sel[0]]
        self.current_contact = c
        self._populate_fields(c)
        self._set_buttons_state(parsed=True)

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
