import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class TitleEditDialog(simpledialog.Dialog):
    """
    Allgemeiner Dialog zum Hinzufügen/Bearbeiten eines Titels
    mit Feldern 'Langform' und 'Kurzform'.
    """

    def __init__(self, parent, title: str, langform: str = "", kurzform: str = ""):
        self.initial_lang = langform
        self.initial_kurz = kurzform
        self.result: tuple[str, str] | None = None
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="Langform:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.lang_var = tk.StringVar(value=self.initial_lang)
        ttk.Entry(master, textvariable=self.lang_var, width=40).grid(
            row=0, column=1, padx=5, pady=5
        )

        ttk.Label(master, text="Kurzform:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        self.kurz_var = tk.StringVar(value=self.initial_kurz)
        ttk.Entry(master, textvariable=self.kurz_var, width=40).grid(
            row=1, column=1, padx=5, pady=5
        )
        return None  # initial focus

    def apply(self):
        lang = self.lang_var.get().strip()
        kurz = self.kurz_var.get().strip()
        if lang and kurz:
            self.result = (lang, kurz)


class TitleManagerDialog:
    """
    Dialog zum komfortablen Hinzufügen, Bearbeiten, Löschen
    und Zurücksetzen aller Titel in titles.json.
    """

    def __init__(self, parent: tk.Tk, repo):
        self.repo = repo
        self.repo.load()
        self.win = tk.Toplevel(parent)
        self.win.title("Titelverwaltung")
        self.win.geometry("450x350")
        self._build_ui()
        self._load_items()

    def _build_ui(self):
        cols = ("Langform", "Kurzform")
        self.tree = ttk.Treeview(
            self.win, columns=cols, show="headings", selectmode="browse"
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Hinzufügen", command=self._add).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Bearbeiten", command=self._edit).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Löschen", command=self._delete).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Zurücksetzen", command=self._reset).pack(
            side=tk.RIGHT
        )

    def _load_items(self):
        self.tree.delete(*self.tree.get_children())
        for lang, kurz in sorted(self.repo.titles.items()):
            self.tree.insert("", tk.END, values=(lang, kurz))

    def _add(self):
        dlg = TitleEditDialog(self.win, "Neuen Titel hinzufügen")
        if dlg.result:
            lang, kurz = dlg.result
            if self.repo.add(lang, kurz):
                self._load_items()
            else:
                messagebox.showinfo(
                    "Unverändert", "Dieser Titel ist bereits so vorhanden."
                )

    def _edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Keine Auswahl", "Bitte einen Titel auswählen.")
            return
        lang, kurz = self.tree.item(sel[0], "values")
        dlg = TitleEditDialog(self.win, "Titel bearbeiten", lang, kurz)
        if dlg.result:
            new_lang, new_kurz = dlg.result
            # Wenn sich die Langform geändert hat, alten Eintrag entfernen
            if new_lang != lang:
                self.repo.delete(lang)
            if self.repo.add(new_lang, new_kurz):
                self._load_items()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Keine Auswahl", "Bitte einen Titel auswählen.")
            return
        lang = self.tree.item(sel[0], "values")[0]
        if messagebox.askyesno(
            "Löschen", f"Titel '{lang}' wirklich löschen?", parent=self.win
        ):
            if self.repo.delete(lang):
                self._load_items()

    def _reset(self):
        if messagebox.askyesno(
            "Zurücksetzen",
            "Alle Titel werden auf Werkseinstellungen zurückgesetzt.\nFortfahren?",
            parent=self.win,
        ):
            self.repo.reset_to_defaults()
            self._load_items()
