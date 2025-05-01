from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import _tkinter
import pyperclip
import ttkthemes
import os
import shlex # For safe splitting later if needed

from .config.settings import Settings
from .ui.styles import Styles
from .ui.components import UIComponents
from .ui.preferences_dialog import PreferencesDialog
from .ui.delete_dialog import DeleteDialog 
from .utils.logger import setup_logger
from .utils.file_handler import FileHandler, DEFAULT_EXCLUDE_PATTERNS 

from .utils.nodo import Nodo


class ConvertidorDirectorios:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Convertidor de Estructuras | Por HabunoGD1809")

        self.settings = Settings()
        self.logger = setup_logger()
        self.styles = Styles(self.settings)

        self.style = ttkthemes.ThemedStyle(self.window)
        self._set_initial_theme()

        # --- Variables de Control ---
        self.usar_iconos = tk.BooleanVar(value=self.settings.get('usar_iconos', True))
        self.estructura_actual = ""
        self._ultimo_directorio = None # Suggestion for dialogs
        self.ignore_patterns_var = tk.StringVar(value="") # For generation

        self.aplicar_tema()
        self.setup_ui()

    def _set_initial_theme(self):
        """Sets the initial theme, falling back on error."""
        initial_theme_setting = self.settings.get('theme', 'dark')
        theme_to_try = "equilux" if initial_theme_setting == "dark" else "arc"
        fallback_theme = 'clam'
        try:
            self.logger.info(f"Intentando establecer tema inicial ttk: '{theme_to_try}'")
            self.style.set_theme(theme_to_try)
            self.logger.info(f"Tema ttk inicial establecido a: '{theme_to_try}'")
        except _tkinter.TclError as e:
            self.logger.warning(f"No se pudo establecer el tema ttk '{theme_to_try}': {e}. Usando fallback '{fallback_theme}'.")
            try:
                self.style.set_theme(fallback_theme)
                self.logger.info(f"Tema ttk inicial establecido a fallback: '{fallback_theme}'")
            except _tkinter.TclError as e_fallback:
                self.logger.error(f"No se pudo establecer el tema ttk de fallback '{fallback_theme}': {e_fallback}.")

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.styles.configure_styles(self.style)
        self.main_frame = ttk.Frame(self.window, padding="20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        callbacks = {
            'actualizar_preview': self.actualizar_preview,
            'convertir_directorio': self.convertir_directorio,
            'crear_desde_estructura': self.crear_desde_estructura,
            'copiar_estructura': self.copiar_estructura,
            'guardar_estructura': self.guardar_estructura,
            'abrir_preferencias': self.abrir_preferencias,
            'abrir_dialogo_limpieza': self.abrir_dialogo_limpieza # Still triggers dialog opening
        }

        self.ui = UIComponents(self.main_frame, self.styles, callbacks)

        # Packing order adjusted in previous step, should be correct now
        self.ui.create_title_section()
        self.ui.create_options_section(self.usar_iconos, self.ignore_patterns_var)
        self.ui.create_buttons_section()

        footer_frame = self.ui.create_footer()
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        action_buttons_frame = self.ui.create_action_buttons()
        action_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 5))

        preview_container, self.preview_text = self.ui.create_preview_section()
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    def aplicar_tema(self):
        """Aplica el tema actual y configuraciones de fuente"""
        theme_name_setting = self.settings.get('theme', 'dark')
        theme_to_set = "equilux" if theme_name_setting == "dark" else "arc"
        fallback_theme = 'clam'
        try:
            current_theme = self.style.theme_use()
            if current_theme != theme_to_set:
                self.logger.info(f"Intentando cambiar tema ttk a: '{theme_to_set}'")
                self.style.set_theme(theme_to_set)
                self.logger.info(f"Tema ttk cambiado a: '{theme_to_set}'")
        except _tkinter.TclError as e:
             self.logger.warning(f"No se pudo cambiar tema ttk a '{theme_to_set}': {e}. Usando fallback '{fallback_theme}'.")
             try:
                 if self.style.theme_use() != fallback_theme:
                     self.style.set_theme(fallback_theme)
                     self.logger.info(f"Tema ttk cambiado a fallback: '{fallback_theme}'")
             except _tkinter.TclError as e_fallback:
                  self.logger.error(f"No se pudo establecer tema ttk fallback '{fallback_theme}': {e_fallback}.")

        self.styles.update_theme(theme_name_setting)
        theme_colors = self.styles.current_theme
        self.window.configure(bg=theme_colors['bg_color'])

        if hasattr(self, 'preview_text') and self.preview_text:
            text_config = self.styles.get_text_widget_config()
            self.preview_text.configure(**text_config)
            self._update_placeholder_color()

        if hasattr(self, 'style'): self.styles.configure_styles(self.style)

        if hasattr(self, 'main_frame'):
             for widget in self.main_frame.winfo_children():
                 try:
                     if isinstance(widget, (ttk.Frame, ttk.LabelFrame, ttk.Button, ttk.Checkbutton, ttk.Label, ttk.Entry)):
                         widget_style = widget.cget('style')
                         if widget_style: widget.configure(style=widget_style)
                         if isinstance(widget, ttk.Entry) and hasattr(self, 'ui'):
                              font = (self.styles.settings.get('ui_font_family', 'Segoe UI'), self.styles.settings.get('ui_font_size', 10))
                              widget.configure(font=font)
                 except tk.TclError: pass
             if hasattr(self, 'preview_text') and self.preview_text:
                 text_config = self.styles.get_text_widget_config()
                 self.preview_text.configure(bg=text_config['bg'], fg=text_config['fg'])
                 self._update_placeholder_color()

    def _update_placeholder_color(self):
         if hasattr(self, 'preview_text') and self.preview_text and self.preview_text.winfo_exists():
            content = self.preview_text.get("1.0", "end-1c").strip()
            if content == self.ui.preview_placeholder: self.preview_text.configure(fg='grey50')
            else: self.preview_text.configure(fg=self.styles.current_theme['preview_fg'])

    def abrir_preferencias(self):
        def aplicar_cambios():
            self.aplicar_tema()
            self.logger.info("Preferencias actualizadas y tema aplicado")
            if hasattr(self, 'ui'): self.ui.show_message("✨ Preferencias actualizadas correctamente", "success")
        PreferencesDialog(self.window, self.settings, self.styles, aplicar_cambios)

    def _get_preview_content(self):
        if not hasattr(self, 'preview_text') or not self.preview_text or not self.preview_text.winfo_exists(): return ""
        content = self.preview_text.get("1.0", tk.END).strip()
        return "" if content == self.ui.preview_placeholder else content

    def _get_combined_ignore_patterns(self) -> list[str]:
        custom_patterns_str = self.ignore_patterns_var.get().strip()
        custom_patterns = [p.strip() for p in custom_patterns_str.split(',') if p.strip()] if custom_patterns_str else []
        combined_patterns = list(set(DEFAULT_EXCLUDE_PATTERNS + custom_patterns))
        self.logger.debug(f"Patrones de ignorados combinados: {combined_patterns}")
        return combined_patterns

    def convertir_directorio(self):
        try:
            dir_path = filedialog.askdirectory(title="Seleccionar Directorio")
            if not dir_path or not os.path.isdir(dir_path): return
            self.logger.info(f"Procesando directorio: {dir_path}")
            self._ultimo_directorio = dir_path
            exclude_patterns = self._get_combined_ignore_patterns()
            self._regenerar_estructura_actual(exclude_patterns=exclude_patterns)

            if self.estructura_actual in ["📂 Directorio vacío", "└── Directorio vacío"]:
                self.ui.show_message("⚠️ El directorio seleccionado está vacío o todo su contenido fue ignorado.", "warning")
                self.actualizar_preview()
                return
            elif "🚫" in self.estructura_actual or "❌" in self.estructura_actual:
                 self.ui.show_message("⚠️ Errores al leer algunos elementos (ver estructura).", "warning", 5000)

            self.actualizar_preview()
            if "🚫" not in self.estructura_actual and "❌" not in self.estructura_actual:
                self.ui.show_message("✅ Estructura generada correctamente", "success")
            self.logger.info("Generación de estructura completada.")
        except PermissionError: self.logger.error(f"Permiso denegado: {dir_path}"); self.ui.show_message(f"❌ Permiso denegado: {dir_path}", "error", 5000)
        except Exception as e: self.logger.error(f"Error convirtiendo dir: {e}", exc_info=True); self.ui.show_message(f"❌ Error procesando: {e}", "error", 5000)

    def _regenerar_estructura_actual(self, exclude_patterns: list[str] | None = None):
        if exclude_patterns is None: exclude_patterns = self._get_combined_ignore_patterns()
        if hasattr(self, '_ultimo_directorio') and self._ultimo_directorio and os.path.isdir(self._ultimo_directorio):
            try:
                self.logger.info(f"Regenerando: {self._ultimo_directorio} (Iconos: {self.usar_iconos.get()}) Ignorando: {exclude_patterns}")
                gen_func = FileHandler.generar_estructura_iconos if self.usar_iconos.get() else FileHandler.generar_estructura_arbol
                self.estructura_actual = gen_func(self._ultimo_directorio, exclude_patterns=exclude_patterns)
                self.logger.info(f"Regenerada (inicio):\n{self.estructura_actual[:200]}...")
            except PermissionError: self.logger.error(f"Permiso denegado regenerando: {self._ultimo_directorio}"); self.estructura_actual = "Error de permisos."
            except Exception as e: self.logger.error(f"Error regenerando: {e}", exc_info=True); self.estructura_actual = "Error inesperado."
        else: self.estructura_actual = ""; self.logger.info("No hay dir cargado.")

    def crear_desde_estructura(self):
        try:
            estructura = self._get_preview_content();
            if not estructura: self.ui.show_message("⚠️ No hay estructura para crear.", "warning"); return
            is_valid, msg = FileHandler.validar_estructura_para_creacion(estructura)
            if not is_valid: self.ui.show_message(f"❌ {msg}", "error", 6000); return
            dest_dir = filedialog.askdirectory(title="Directorio Destino para Crear Estructura");
            if not dest_dir: return
            confirm = messagebox.askyesno("Confirmar Creación", f"Crear estructura en:\n{dest_dir}\n\n¿Continuar?", parent=self.window)
            if not confirm: return
            self.logger.info(f"Creando estructura en: {dest_dir}")
            if Nodo.crear_desde_texto(estructura, dest_dir): self.logger.info("Creada exitosamente"); self.ui.show_message("✅ Estructura creada", "success")
            else: self.ui.show_message("❌ Error al crear. Revisa logs.", "error", 5000)
        except ValueError as ve: self.logger.error(f"Error validación: {ve}"); self.ui.show_message(f"⚠️ {ve}", "warning", 5000)
        except PermissionError as pe: self.logger.error(f"Permiso denegado creando en: {dest_dir}. {pe}"); self.ui.show_message(f"❌ Permiso denegado creando", "error", 5000)
        except FileNotFoundError as fnf: self.logger.error(f"Dir base no encontrado: {fnf}"); self.ui.show_message(f"❌ Dir base no encontrado", "error", 5000)
        except Exception as e: self.logger.error(f"Error creando: {e}", exc_info=True); self.ui.show_message(f"❌ Error inesperado creando: {e}", "error", 5000)

    def actualizar_preview(self, from_checkbox=False):
        if not hasattr(self, 'preview_text') or not self.preview_text or not self.preview_text.winfo_exists(): return
        current_content = self._get_preview_content()
        if from_checkbox and hasattr(self, '_ultimo_directorio') and self._ultimo_directorio:
             self._regenerar_estructura_actual() # Uses current ignores
        display_content = self.estructura_actual if self.estructura_actual else current_content
        try:
            self.preview_text.configure(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            if display_content: self.preview_text.insert("1.0", display_content); self._update_placeholder_color()
            else: self.preview_text.insert("1.0", self.ui.preview_placeholder); self.preview_text.configure(fg='grey50')
        except Exception as e: self.logger.error(f"Error actualizando preview: {e}", exc_info=True)

    def copiar_estructura(self):
        try:
            content = self.estructura_actual if self.estructura_actual else self._get_preview_content()
            if content: self.window.clipboard_clear(); self.window.clipboard_append(content); self.window.update(); self.ui.show_message("✅ Copiada", "success")
            else: self.ui.show_message("⚠️ Nada que copiar", "warning")
        except Exception as e: self.logger.error(f"Error copiando: {e}", exc_info=True); self.ui.show_message("❌ Error al copiar", "error")

    def guardar_estructura(self):
        try:
            content = self.estructura_actual if self.estructura_actual else self._get_preview_content()
            if not content: self.ui.show_message("⚠️ Nada que guardar", "warning"); return
            is_valid, _ = FileHandler.validar_estructura_para_creacion(content)
            if not is_valid:
                if not messagebox.askyesno("Advertencia", "Formato inválido.\n¿Guardar?", icon='warning', parent=self.window): return
            filename = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md"), ("Texto", "*.txt"), ("Todos", "*.*")], title="Guardar Como...", initialdir=os.getcwd(), initialfile="estructura.md")
            if filename: FileHandler.guardar_estructura(filename, content, self.usar_iconos.get()); self.ui.show_message(f"✅ Guardada: {os.path.basename(filename)}", "success")
        except Exception as e: self.logger.error(f"Error guardando: {e}", exc_info=True); self.ui.show_message(f"❌ Error al guardar: {e}", "error", 5000)

    # --- MODIFIED: Opens dialog without checking _ultimo_directorio first ---
    def abrir_dialogo_limpieza(self):
        """Abre el diálogo para configurar y ejecutar la limpieza, permitiendo seleccionar directorio."""
        self.logger.info("Abriendo diálogo de limpieza.")
        # Pass the last directory as a suggestion (can be None)
        dialog = DeleteDialog(self.window, self._ultimo_directorio, self._ejecutar_limpieza, self.styles)
        # The dialog now handles everything else, including getting the target dir

    def _ejecutar_limpieza(self, target_dir: str, options: dict):
        """ Ejecuta la lógica de limpieza real después de la confirmación en el diálogo. """
        # This method remains largely the same, as the dialog now prepares the 'options'
        # and ensures 'target_dir' is valid before calling this.
        if not target_dir or not os.path.isdir(target_dir):
            self.logger.error(f"Intento de ejecutar limpieza en directorio inválido: {target_dir}")
            self.ui.show_message("❌ El directorio de destino para la limpieza no es válido.", "error")
            return
        self.logger.info(f"Ejecutando limpieza para: {target_dir} con opciones: {options}")
        try:
            # Note: The 'ignore_patterns' are applied inside encontrar_archivos_para_limpiar called by the dialog now.
            # We just execute the deletion based on the filtered list implicitly handled before this callback.
            deleted_count, error_count = FileHandler.limpiar_directorio(
                target_dir,
                options.get('clean_pycache', False),
                options.get('clean_logs', False),
                options.get('custom', []),
                confirmed=True # Confirmation happened in dialog
            )
            message = f"✅ Limpieza completada. {deleted_count} elementos eliminados."
            msg_type = "success"
            if error_count > 0: message += f" ⚠️ {error_count} errores (ver log)."; msg_type = "warning"
            self.ui.show_message(message, msg_type, duration=5000)
            self.logger.info(f"Limpieza finalizada. Eliminados: {deleted_count}, Errores: {error_count}")
            # Refresh main view ONLY if the cleaned directory is the one currently loaded
            if target_dir == self._ultimo_directorio:
                 self.logger.info("Refrescando vista después de limpieza.")
                 self._regenerar_estructura_actual() # Use current generation ignores
                 self.actualizar_preview()
        except PermissionError as pe: self.logger.error(f"Permiso denegado limpieza {target_dir}: {pe}", exc_info=True); self.ui.show_message(f"❌ Permiso denegado durante limpieza.", "error", 5000)
        except Exception as e: self.logger.error(f"Error inesperado limpieza: {e}", exc_info=True); self.ui.show_message(f"❌ Error inesperado limpieza: {e}", "error", 5000)

    def run(self):
        """Inicia la aplicación"""
        self.logger.info("Iniciando aplicación")
        try: # Apply geometry
            geom = self.settings.get('window_size', '1000x700')
            if '+' in geom: self.window.geometry(geom)
            elif 'x' in geom:
                 parts = geom.split('x')
                 if len(parts)==2 and parts[0].isdigit() and parts[1].isdigit():
                      w, h = int(parts[0]), int(parts[1])
                      sw, sh = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
                      x, y = max(0,(sw-w)//2), max(0,(sh-h)//2)
                      self.window.geometry(f"{w}x{h}+{x}+{y}")
                 else: self.window.geometry('1000x700'); self.window.eval('tk::PlaceWindow . center')
            else: self.window.geometry('1000x700'); self.window.eval('tk::PlaceWindow . center')
        except Exception as e: self.logger.error(f"Error geometría: {e}", exc_info=True); self.window.geometry('1000x700'); self.window.eval('tk::PlaceWindow . center')

        self.window.after(500, lambda: self.ui.show_message("👋 ¡Bienvenido!", "info", 5000))
        def on_closing():
            try: # Save settings
                self.logger.info("Cerrando y guardando config...")
                self.settings.set('usar_iconos', self.usar_iconos.get())
                geom = self.window.geometry(); size = geom.split('+')[0]
                if 'x' in size: self.settings.set('window_size', size)
                self.settings.save_settings(); self.logger.info("Config guardada.")
            except Exception as e: self.logger.error(f"Error guardando config: {e}")
            finally: self.logger.info("Destruyendo ventana."); self.window.destroy(); self.logger.info("App cerrada.")
        self.window.protocol("WM_DELETE_WINDOW", on_closing)
        self.window.mainloop()
