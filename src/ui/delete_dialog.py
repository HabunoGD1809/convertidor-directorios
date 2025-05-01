from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging

from src.utils.file_handler import FileHandler

logger = logging.getLogger('ConvertidorDirectorios')

class DeleteDialog(tk.Toplevel):
    def __init__(self, parent, initial_dir: str | None, execute_callback: callable, styles):
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
        """Configura la interfaz del diálogo de limpieza."""
        main_frame = ttk.Frame(self, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True) # Main frame fills the dialog

        # --- Pack top/middle content first ---
        target_frame = ttk.LabelFrame(main_frame, text="Directorio a Limpiar", padding="10", style='TLabelframe')
        target_frame.pack(fill=tk.X, pady=(0, 10)) # Reduced bottom padding

        self.dir_entry = ttk.Entry(
            target_frame,
            textvariable=self.selected_dir_var,
            style='TEntry',
            font=(self.styles.settings.get('ui_font_family'), self.styles.settings.get('ui_font_size'))
        )
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_button = ttk.Button(
            target_frame, text="Seleccionar...", style='Custom.TButton', command=self._select_directory
        )
        browse_button.pack(side=tk.LEFT)

        options_frame = ttk.LabelFrame(main_frame, text="Opciones de Limpieza (Qué eliminar)", padding="10", style='TLabelframe')
        options_frame.pack(fill=tk.X, pady=(0, 10)) # Reduced bottom padding
        checkbox_frame = ttk.Frame(options_frame, style='TFrame'); checkbox_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="`__pycache__`", variable=self.limpiar_pycache_var, style='TCheckbutton').pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(checkbox_frame, text="`.log`", variable=self.limpiar_logs_var, style='TCheckbutton').pack(side=tk.LEFT)
        custom_frame = ttk.Frame(options_frame, style='TFrame'); custom_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(custom_frame, text="Patrones personalizados:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        entry_font = (self.styles.settings.get('ui_font_family'), self.styles.settings.get('ui_font_size'))
        ttk.Entry(custom_frame, textvariable=self.patrones_personalizados_var, width=35, font=entry_font).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ignore_frame = ttk.LabelFrame(main_frame, text="Opciones de Exclusión (Qué NO eliminar)", padding="10", style='TLabelframe')
        ignore_frame.pack(fill=tk.X, pady=(0, 15)) # Keep padding below ignore frame
        ttk.Label(ignore_frame, text="Ignorar patrones (coma-separado):", style='Custom.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        ignore_entry = ttk.Entry(
            ignore_frame, textvariable=self.ignore_patterns_var, font=entry_font, width=40
        )
        ignore_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Pack Action Buttons LAST, using side=BOTTOM ---
        button_frame = ttk.Frame(main_frame, style='TFrame')
        # Pack this frame at the bottom of main_frame
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Pack buttons inside the button_frame (order matters for side=tk.RIGHT)
        # Cancel button packed last appears furthest right
        self.cancel_button = ttk.Button(
            button_frame, text="Cancelar", style='Custom.TButton', command=self._on_cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0)) # Padding on the left

        # Find button packed before Cancel appears to its left
        self.find_button = ttk.Button(
            button_frame, text="Buscar y Confirmar Eliminación...", style='Custom.TButton', command=self._buscar_y_confirmar
        )
        self.find_button.pack(side=tk.RIGHT, padx=(0, 5)) # Padding on the right


    def _select_directory(self):
        """Abre el diálogo para seleccionar un directorio."""
        initial_dir = self.selected_dir_var.get() or os.getcwd()
        dir_path = filedialog.askdirectory(
            title="Seleccionar Directorio para Limpiar",
            initialdir=initial_dir,
            parent=self
            )
        if dir_path:
            self.selected_dir_var.set(dir_path)
            logger.info(f"Directorio seleccionado para limpieza: {dir_path}")


    def _buscar_y_confirmar(self):
        """Busca archivos, aplica ignorados, muestra confirmación y ejecuta si se confirma."""
        target_dir = self.selected_dir_var.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Selecciona un directorio válido para limpiar.", parent=self)
            return

        clean_pycache = self.limpiar_pycache_var.get()
        clean_logs = self.limpiar_logs_var.get()
        custom_patterns = [p.strip() for p in self.patrones_personalizados_var.get().split(',') if p.strip()]
        ignore_patterns = [p.strip() for p in self.ignore_patterns_var.get().split(',') if p.strip()]
        logger.debug(f"Patrones ignorados limpieza: {ignore_patterns}")

        if not clean_pycache and not clean_logs and not custom_patterns:
            messagebox.showinfo("Sin Opciones", "No se seleccionaron opciones de qué eliminar.", parent=self)
            return

        try:
            logger.info(f"Buscando en: {target_dir}, ignorando: {ignore_patterns}")
            items_to_delete = FileHandler.encontrar_archivos_para_limpiar(
                target_dir, clean_pycache, clean_logs, custom_patterns, ignore_patterns=ignore_patterns
            )

            if not items_to_delete:
                messagebox.showinfo("Limpieza", "No se encontraron elementos (respetando ignorados).", parent=self)
                logger.info("No elementos a limpiar.")
                return

            confirm_message = f"Eliminar {len(items_to_delete)} elementos de '{os.path.basename(target_dir)}' (respetando ignorados):\n\n"
            preview = [os.path.relpath(item, target_dir) for item in items_to_delete[:15]]
            confirm_message += "\n".join(f"- {p}" for p in preview)
            if len(items_to_delete) > 15: confirm_message += f"\n... y {len(items_to_delete) - 15} más."
            confirm_message += "\n\n⚠️ ¡ESTA ACCIÓN NO SE PUEDE DESHACER! ⚠️\n\n¿Continuar?"
            confirm = messagebox.askyesno("Confirmar Limpieza PERMANENTE", confirm_message, icon='warning', parent=self)

            if confirm:
                logger.info("Usuario confirmó eliminación.")
                options = {'clean_pycache': clean_pycache, 'clean_logs': clean_logs, 'custom': custom_patterns}
                self.execute_callback(target_dir, options)
                self.destroy()
            else:
                logger.info("Usuario canceló eliminación.")

        except PermissionError as pe:
             logger.error(f"Error permisos buscando en {target_dir}: {pe}", exc_info=True)
             messagebox.showerror("Error", f"Error permisos buscando en:\n{target_dir}", parent=self)
        except Exception as e:
            logger.error(f"Error buscando/confirmando limpieza: {e}", exc_info=True)
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}", parent=self)

    def _on_cancel(self):
        """Cierra el diálogo sin hacer nada."""
        logger.debug("Diálogo limpieza cancelado.")
        self.destroy()
