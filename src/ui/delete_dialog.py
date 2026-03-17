from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from typing import Callable

from src.utils.file_handler import FileHandler
from .custom_widgets import TagEntry

logger = logging.getLogger('ConvertidorDirectorios')

class DeleteDialog(tk.Toplevel):
    def __init__(self, parent, initial_dir: str | None, execute_callback: Callable, styles):
        super().__init__(parent)
        self.selected_dir_var = tk.StringVar(value=initial_dir or "")
        self.execute_callback = execute_callback
        self.styles = styles

        self.title("Limpiar Directorio")
        self.geometry("650x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.limpiar_pycache_var = tk.BooleanVar(value=True)
        self.limpiar_logs_var = tk.BooleanVar(value=True)
        self.patrones_personalizados_var = tk.StringVar(value="")
        self.ignore_patterns_var = tk.StringVar(value="")

        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True) 

        target_frame = ttk.LabelFrame(main_frame, text="Directorio a Limpiar", padding="10", style='TLabelframe')
        target_frame.pack(fill=tk.X, pady=(0, 10)) 

        ui_font_family = self.styles.settings.get('ui_font_family') or 'Segoe UI'
        ui_font_size = self.styles.settings.get('ui_font_size') or 10
        entry_font = (ui_font_family, ui_font_size)

        self.dir_entry = ttk.Entry(
            target_frame,
            textvariable=self.selected_dir_var,
            style='TEntry',
            font=entry_font
        )
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_button = ttk.Button(
            target_frame, text="Seleccionar...", style='Custom.TButton', command=self._select_directory
        )
        browse_button.pack(side=tk.LEFT)

        options_frame = ttk.LabelFrame(main_frame, text="Opciones de Limpieza (Qué eliminar)", padding="10", style='TLabelframe')
        options_frame.pack(fill=tk.X, pady=(0, 10)) 
        
        checkbox_frame = ttk.Frame(options_frame, style='TFrame')
        checkbox_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="`__pycache__`", variable=self.limpiar_pycache_var, style='TCheckbutton').pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(checkbox_frame, text="`.log`", variable=self.limpiar_logs_var, style='TCheckbutton').pack(side=tk.LEFT)
        
        custom_frame = ttk.Frame(options_frame, style='TFrame')
        custom_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(custom_frame, text="Patrones personalizados:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        custom_patterns_entry = TagEntry(custom_frame, self.patrones_personalizados_var, self.styles)
        custom_patterns_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ignore_frame = ttk.LabelFrame(main_frame, text="Opciones de Exclusión (Qué NO eliminar)", padding="10", style='TLabelframe')
        ignore_frame.pack(fill=tk.X, pady=(0, 15)) 
        ttk.Label(ignore_frame, text="Ignorar patrones:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        ignore_entry = TagEntry(ignore_frame, self.ignore_patterns_var, self.styles)
        ignore_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.cancel_button = ttk.Button(
            button_frame, text="Cancelar", style='Custom.TButton', command=self._on_cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.find_button = ttk.Button(
            button_frame, text="Buscar y Confirmar...", style='Custom.TButton', command=self._buscar_y_confirmar
        )
        self.find_button.pack(side=tk.RIGHT, padx=(0, 5))

    def _select_directory(self):
        initial_dir = self.selected_dir_var.get() or os.getcwd()
        dir_path = filedialog.askdirectory(
            title="Seleccionar Directorio para Limpiar",
            initialdir=initial_dir,
            parent=self
            )
        if dir_path:
            self.selected_dir_var.set(dir_path)

    def _buscar_y_confirmar(self):
        target_dir = self.selected_dir_var.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Selecciona un directorio válido.", parent=self)
            return

        clean_pycache = self.limpiar_pycache_var.get()
        clean_logs = self.limpiar_logs_var.get()
        custom_patterns = [p.strip() for p in self.patrones_personalizados_var.get().split(',') if p.strip()]
        ignore_patterns = [p.strip() for p in self.ignore_patterns_var.get().split(',') if p.strip()]

        if not clean_pycache and not clean_logs and not custom_patterns:
            messagebox.showinfo("Sin Opciones", "No se seleccionaron opciones de qué eliminar.", parent=self)
            return

        try:
            items_to_delete = FileHandler.encontrar_archivos_para_limpiar(
                target_dir, clean_pycache, clean_logs, custom_patterns, ignore_patterns=ignore_patterns
            )

            if not items_to_delete:
                messagebox.showinfo("Limpieza", "No se encontraron elementos.", parent=self)
                return

            confirm_message = f"Eliminar {len(items_to_delete)} elementos:\n\n"
            preview = [os.path.relpath(item, target_dir) for item in items_to_delete[:15]]
            confirm_message += "\n".join(f"- {p}" for p in preview)
            if len(items_to_delete) > 15: confirm_message += f"\n... y {len(items_to_delete) - 15} más."
            confirm_message += "\n\n⚠️ ¡ESTA ACCIÓN NO SE PUEDE DESHACER! ⚠️\n\n¿Continuar?"
            confirm = messagebox.askyesno("Confirmar Limpieza", confirm_message, icon='warning', parent=self)

            if confirm:
                options = {'clean_pycache': clean_pycache, 'clean_logs': clean_logs, 'custom': custom_patterns, 'ignore_patterns': ignore_patterns}
                self.execute_callback(target_dir, options)
                self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}", parent=self)

    def _on_cancel(self):
        self.destroy()
