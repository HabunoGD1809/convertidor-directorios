from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import _tkinter
import os

from .config.settings import Settings
from .ui.styles import Styles
from .ui.components import UIComponents
from .ui.preferences_dialog import PreferencesDialog
from .ui.delete_dialog import DeleteDialog 
from .utils.logger import setup_logger
from .utils.file_handler import FileHandler
from .utils.nodo import Nodo


class ConvertidorDirectorios:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Convertidor de Estructuras | Por HabunoGD1809")

        self.settings = Settings()
        self.logger = setup_logger()
        self.styles = Styles(self.settings)

        try:
            from ttkthemes import ThemedStyle
            self.style = ThemedStyle(self.window)
        except ImportError:
            self.logger.warning("ttkthemes no instalado. Usando estilo por defecto.")
            self.style = ttk.Style(self.window)
        
        self._set_initial_theme()

        self.usar_iconos = tk.BooleanVar(value=self.settings.get('usar_iconos', True))
        
        patrones_raw = self.settings.get('ignore_patterns', [])
        patrones_guardados = patrones_raw if isinstance(patrones_raw, list) else []
        self.ignore_patterns_var = tk.StringVar(value=",".join(str(p) for p in patrones_guardados))
        
        self.guardar_patrones_var = tk.BooleanVar(value=self.settings.get('guardar_patrones', True))
        
        self.estructura_actual = ""
        self._ultimo_directorio = None 

        self.aplicar_tema()
        self.setup_ui()

    def _set_initial_theme(self):
        initial_theme_setting = self.settings.get('theme', 'dark')
        theme_to_try = "equilux" if initial_theme_setting == "dark" else "arc"
        fallback_theme = 'clam'
        try:
            if hasattr(self.style, 'set_theme'):
                getattr(self.style, 'set_theme')(theme_to_try)
        except _tkinter.TclError:
            try:
                if hasattr(self.style, 'theme_use'):
                     self.style.theme_use(fallback_theme)
            except _tkinter.TclError: pass

    def setup_ui(self):
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
            'abrir_dialogo_limpieza': self.abrir_dialogo_limpieza 
        }

        self.ui = UIComponents(self.main_frame, self.styles, callbacks)

        self.ui.create_title_section()
        self.ui.create_options_section(self.usar_iconos, self.ignore_patterns_var, self.guardar_patrones_var)
        self.ui.create_buttons_section()

        footer_frame = self.ui.create_footer()
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        action_buttons_frame = self.ui.create_action_buttons()
        action_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 5))

        preview_container, self.preview_text = self.ui.create_preview_section()
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    def aplicar_tema(self):
        theme_name_setting = self.settings.get('theme', 'dark')
        theme_to_set = "equilux" if theme_name_setting == "dark" else "arc"
        fallback_theme = 'clam'
        try:
            if hasattr(self.style, 'theme_use') and self.style.theme_use() != theme_to_set:
                if hasattr(self.style, 'set_theme'): getattr(self.style, 'set_theme')(theme_to_set)
                else: self.style.theme_use(theme_to_set)
        except _tkinter.TclError:
             try:
                 if self.style.theme_use() != fallback_theme: self.style.theme_use(fallback_theme)
             except _tkinter.TclError: pass

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
                              font_family = str(self.styles.settings.get('ui_font_family', 'Segoe UI') or 'Segoe UI')
                              font_size = int(self.styles.settings.get('ui_font_size', 10) or 10)
                              widget.configure(font=(font_family, font_size))
                 except tk.TclError: pass

    def _update_placeholder_color(self):
         if hasattr(self, 'preview_text') and self.preview_text and self.preview_text.winfo_exists():
            content = self.preview_text.get("1.0", "end-1c").strip()
            if content == self.ui.preview_placeholder: self.preview_text.configure(fg='grey50')
            else: self.preview_text.configure(fg=self.styles.current_theme['preview_fg'])

    def abrir_preferencias(self):
        def aplicar_cambios():
            self.aplicar_tema()
            if hasattr(self, 'ui'): self.ui.show_message("✨ Preferencias actualizadas correctamente", "success")
        PreferencesDialog(self.window, self.settings, self.styles, aplicar_cambios)

    def _get_preview_content(self):
        if not hasattr(self, 'preview_text') or not self.preview_text or not self.preview_text.winfo_exists(): return ""
        content = self.preview_text.get("1.0", tk.END).strip()
        return "" if content == self.ui.preview_placeholder else content

    def _get_combined_ignore_patterns(self) -> list[str]:
        custom_patterns_str = self.ignore_patterns_var.get().strip()
        return [p.strip() for p in custom_patterns_str.split(',') if p.strip()] if custom_patterns_str else []

    def convertir_directorio(self):
        dir_path = ""
        try:
            dir_path = filedialog.askdirectory(title="Seleccionar Directorio")
            if not dir_path or not os.path.isdir(dir_path): return
            self._ultimo_directorio = dir_path
            exclude_patterns = self._get_combined_ignore_patterns()
            self._regenerar_estructura_actual(exclude_patterns=exclude_patterns)

            if self.estructura_actual in ["📂 Directorio vacío", "└── Directorio vacío"]:
                self.ui.show_message("⚠️ El directorio seleccionado está vacío o todo su contenido fue ignorado.", "warning")
                self.actualizar_preview()
                return
            elif "🚫" in self.estructura_actual or "❌" in self.estructura_actual:
                 self.ui.show_message("⚠️ Errores al leer elementos.", "warning", 5000)

            self.actualizar_preview()
            if "🚫" not in self.estructura_actual and "❌" not in self.estructura_actual:
                self.ui.show_message("✅ Estructura generada", "success")
        except Exception as e: self.ui.show_message(f"❌ Error procesando: {e}", "error", 5000)

    def _regenerar_estructura_actual(self, exclude_patterns: list[str] | None = None):
        if exclude_patterns is None: exclude_patterns = self._get_combined_ignore_patterns()
        if hasattr(self, '_ultimo_directorio') and self._ultimo_directorio and os.path.isdir(self._ultimo_directorio):
            try:
                gen_func = FileHandler.generar_estructura_iconos if self.usar_iconos.get() else FileHandler.generar_estructura_arbol
                self.estructura_actual = gen_func(self._ultimo_directorio, exclude_patterns=exclude_patterns)
            except Exception: self.estructura_actual = "Error inesperado."
        else: self.estructura_actual = ""

    def crear_desde_estructura(self):
        dest_dir = ""
        try:
            estructura = self._get_preview_content()
            if not estructura: self.ui.show_message("⚠️ No hay estructura para crear.", "warning"); return
            
            is_valid, msg, err_line = FileHandler.validar_estructura_para_creacion(estructura)
            if not is_valid: 
                self.ui.show_message(f"❌ {msg}", "error", 6000)
                if err_line > 0: self.ui.resaltar_error_linea(err_line)
                return
                
            dest_dir = filedialog.askdirectory(title="Directorio Destino")
            if not dest_dir: return
            if not messagebox.askyesno("Confirmar", f"Crear estructura en:\n{dest_dir}\n\n¿Continuar?", parent=self.window): return
            
            if Nodo.crear_desde_texto(estructura, dest_dir): self.ui.show_message("✅ Creada exitosamente", "success")
            else: self.ui.show_message("❌ Error. Revisa logs.", "error", 5000)
                
        except Exception as e: self.ui.show_message(f"❌ Error creando: {e}", "error", 5000)

    def actualizar_preview(self, from_checkbox=False):
        if not hasattr(self, 'preview_text') or not self.preview_text or not self.preview_text.winfo_exists(): return
        if from_checkbox:
            if hasattr(self, '_ultimo_directorio') and self._ultimo_directorio and os.path.isdir(self._ultimo_directorio):
                self._regenerar_estructura_actual()
            else:
                current_text = self._get_preview_content()
                if current_text:
                    try: self.estructura_actual = FileHandler.convertir_estructura_texto(current_text, self.usar_iconos.get())
                    except Exception: self.ui.show_message("❌ Error al convertir.", "error")
                else: self.estructura_actual = ""

        try:
            self.preview_text.configure(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            if self.estructura_actual:
                self.preview_text.insert("1.0", self.estructura_actual)
                self._update_placeholder_color()
            else:
                self.preview_text.insert("1.0", self.ui.preview_placeholder)
                self.preview_text.configure(fg='grey50')
        except Exception: pass

    def copiar_estructura(self):
        try:
            content = self.estructura_actual if self.estructura_actual else self._get_preview_content()
            if content: 
                self.window.clipboard_clear()
                self.window.clipboard_append(content)
                self.window.update()
                self.ui.show_message("✅ Copiada", "success")
            else: self.ui.show_message("⚠️ Nada que copiar", "warning")
        except Exception: self.ui.show_message("❌ Error al copiar", "error")

    def guardar_estructura(self):
        try:
            content = self.estructura_actual if self.estructura_actual else self._get_preview_content()
            if not content: self.ui.show_message("⚠️ Nada que guardar", "warning"); return
            
            is_valid, msg, _ = FileHandler.validar_estructura_para_creacion(content)
            if not is_valid:
                if not messagebox.askyesno("Advertencia", f"Formato inválido ({msg}).\n¿Guardar de todos modos?", icon='warning', parent=self.window): return
                
            filename = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md"), ("Todos", "*.*")], title="Guardar", initialfile="estructura.md")
            if filename: 
                FileHandler.guardar_estructura(filename, content, self.usar_iconos.get())
                self.ui.show_message(f"✅ Guardada: {os.path.basename(filename)}", "success")
        except Exception as e: self.ui.show_message(f"❌ Error al guardar: {e}", "error", 5000)

    def abrir_dialogo_limpieza(self):
        DeleteDialog(self.window, self._ultimo_directorio, self._ejecutar_limpieza, self.styles)

    def _ejecutar_limpieza(self, target_dir: str, options: dict):
        if not target_dir or not os.path.isdir(target_dir): return
        try:
            deleted_count, error_count = FileHandler.limpiar_directorio(
                target_dir, options.get('clean_pycache', False), options.get('clean_logs', False), options.get('custom', []), True, options.get('ignore_patterns', [])
            )
            message = f"✅ Limpieza completada. {deleted_count} eliminados."
            msg_type = "success"
            if error_count > 0: message += f" ⚠️ {error_count} errores."; msg_type = "warning"
            self.ui.show_message(message, msg_type, duration=5000)
            if target_dir == self._ultimo_directorio:
                 self._regenerar_estructura_actual() 
                 self.actualizar_preview()
        except Exception as e: self.ui.show_message(f"❌ Error limpieza: {e}", "error", 5000)

    def run(self):
        try: 
            geom = self.settings.get('window_size', '1000x700')
            if geom and isinstance(geom, str) and ('x' in geom or '+' in geom): self.window.geometry(geom)
            else: self.window.eval('tk::PlaceWindow . center')
        except Exception: 
            self.window.geometry('1000x700')
            self.window.eval('tk::PlaceWindow . center')

        self.window.after(500, lambda: self.ui.show_message("👋 ¡Bienvenido!", "info", 5000))
        
        def on_closing():
            try: 
                self.settings.set('usar_iconos', self.usar_iconos.get())
                geom = self.window.geometry(); size = geom.split('+')[0]
                if 'x' in size: self.settings.set('window_size', size)
                
                guardar = self.guardar_patrones_var.get()
                self.settings.set('guardar_patrones', guardar)
                if guardar:
                    patterns = [p.strip() for p in self.ignore_patterns_var.get().split(',') if p.strip()]
                    self.settings.set('ignore_patterns', patterns)
                
                self.settings.save_settings()
            except Exception: pass
            finally: self.window.destroy()
            
        self.window.protocol("WM_DELETE_WINDOW", on_closing)
        self.window.mainloop()
