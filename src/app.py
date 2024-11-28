import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyperclip
import ttkthemes

from .config.settings import Settings
from .ui.styles import Styles
from .ui.components import UIComponents
from .ui.preferences_dialog import PreferencesDialog
from .utils.logger import setup_logger
from .utils.file_handler import FileHandler, Nodo

class ConvertidorDirectorios:
    def __init__(self):
        # Inicializar la ventana principal
        self.window = tk.Tk()
        self.window.title("Convertidor de Estructuras | Por HabunoGD1809")
        
        # Inicializar componentes principales
        self.settings = Settings()
        self.logger = setup_logger()
        self.styles = Styles(self.settings)
        
        # Configurar tema
        self.style = ttkthemes.ThemedStyle(self.window)
        self.style.set_theme("equilux")
        
        # Variables de control
        self.usar_iconos = tk.BooleanVar(value=self.settings.get('usar_iconos', True))
        self.estructura_actual = ""
        
        # Aplicar tema inicial
        self.aplicar_tema()
        
        # Configurar UI
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar estilos
        self.styles.configure_styles(self.style)
        
        # Frame principal
        self.main_frame = ttk.Frame(self.window, padding="20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear callbacks para los componentes
        callbacks = {
            'actualizar_preview': self.actualizar_preview,
            'convertir_directorio': self.convertir_directorio,
            'crear_desde_estructura': self.crear_desde_estructura,
            'copiar_estructura': self.copiar_estructura,
            'guardar_estructura': self.guardar_estructura,
            'abrir_preferencias': self.abrir_preferencias
        }
        
        # Inicializar componentes UI
        self.ui = UIComponents(self.main_frame, self.styles, callbacks)
        
        # Crear secciones de la UI
        self.ui.create_title_section()
        self.ui.create_options_section(self.usar_iconos)
        self.ui.create_buttons_section()
        _, self.preview_text = self.ui.create_preview_section()
        self.ui.create_action_buttons()
        self.ui.create_footer()

    def aplicar_tema(self):
        """Aplica el tema actual y configuraciones de fuente"""
        theme = self.settings.get('theme', 'dark')
        self.styles.update_theme(theme)
        
        # Aplicar color de fondo a la ventana principal
        theme_colors = self.styles.current_theme
        self.window.configure(bg=theme_colors['bg_color'])
        
        # Actualizar configuraciones de texto si existe
        if hasattr(self, 'preview_text'):
            text_config = self.styles.get_text_widget_config()
            self.preview_text.configure(**text_config)
        
        # Reconfigurar estilos si ya están inicializados
        if hasattr(self, 'style'):
            self.styles.configure_styles(self.style)
            
    def abrir_preferencias(self):
        """Abre el diálogo de preferencias"""
        def aplicar_cambios():
            self.aplicar_tema()
            self.logger.info("Preferencias actualizadas")
            self.ui.show_message("✨ Preferencias actualizadas correctamente", "success")
            
        PreferencesDialog(
            self.window,
            self.settings,
            self.styles,
            aplicar_cambios
        )

    def _get_preview_content(self):
        """Obtiene el contenido del área de preview, ignorando el placeholder"""
        content = self.preview_text.get("1.0", tk.END).strip()
        if content == "Pega aquí tu estructura o carga un directorio...":
            return ""
        return content

    def convertir_directorio(self):
        """Convierte un directorio a estructura"""
        try:
            dir_path = filedialog.askdirectory(title="Seleccionar Directorio")
            if not dir_path:
                return
                
            self.logger.info(f"Procesando directorio: {dir_path}")
            self._ultimo_directorio = dir_path  # Guardar referencia al último directorio
            
            if self.usar_iconos.get():
                estructura = FileHandler.generar_estructura_iconos(dir_path)
            else:
                estructura = FileHandler.generar_estructura_arbol(dir_path)
                
            if estructura in ["📂 Directorio vacío", "└── Directorio vacío"]:
                self.ui.show_message("⚠️ El directorio seleccionado está vacío", "warning")
                return
                
            self.estructura_actual = estructura
            self.actualizar_preview()
            self.ui.show_message("✅ Estructura generada correctamente", "success")
            self.logger.info("Estructura generada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al convertir directorio: {str(e)}")
            self.ui.show_message(f"❌ Error al procesar el directorio: {str(e)}", "error")

    def crear_desde_estructura(self):
        """Crea directorios desde la estructura en el preview"""
        try:
            estructura = self._get_preview_content()
            if not estructura:
                self.ui.show_message("⚠️ No hay estructura para crear. Pega una estructura válida primero.", "warning")
                return
                
            if not FileHandler.validar_estructura_markdown(estructura):
                self.ui.show_message("❌ La estructura no está en formato markdown válido. Usa los símbolos └── y ├── correctamente.", "error")
                return
                
            dest_dir = filedialog.askdirectory(title="Seleccionar Directorio Destino")
            if not dest_dir:
                return
                
            self.logger.info(f"Creando estructura en: {dest_dir}")
            Nodo.crear_estructura(estructura, dest_dir, self.usar_iconos.get())
            self.logger.info("Estructura creada exitosamente")
            self.ui.show_message("✅ Estructura creada correctamente", "success")
            
        except ValueError as ve:
            self.logger.error(f"Error de validación: {str(ve)}")
            self.ui.show_message(f"⚠️ {str(ve)}", "warning")
        except Exception as e:
            self.logger.error(f"Error al crear estructura: {str(e)}")
            self.ui.show_message(f"❌ Error al crear la estructura: {str(e)}", "error")

    def actualizar_preview(self):
        """Actualiza el área de preview"""
        if not hasattr(self, 'preview_text'):
            return
            
        current_text = self._get_preview_content()
        
        # Si tenemos una estructura cargada desde un directorio, regenerarla
        if hasattr(self, '_ultimo_directorio') and self._ultimo_directorio:
            try:
                if self.usar_iconos.get():
                    self.estructura_actual = FileHandler.generar_estructura_iconos(self._ultimo_directorio)
                else:
                    self.estructura_actual = FileHandler.generar_estructura_arbol(self._ultimo_directorio)
            except Exception as e:
                self.logger.error(f"Error regenerando estructura: {str(e)}")
        
        self.preview_text.delete("1.0", tk.END)
        
        if self.estructura_actual:
            self.preview_text.insert("1.0", self.estructura_actual)
            self.preview_text.configure(fg=self.styles.current_theme['preview_fg'])
        elif not current_text:
            self.preview_text.insert("1.0", "Pega aquí tu estructura o carga un directorio...")
            self.preview_text.configure(fg='gray')

    def copiar_estructura(self):
        """Copia la estructura al portapapeles"""
        try:
            estructura = self._get_preview_content()
            if estructura:
                pyperclip.copy(estructura)
                self.logger.info("Estructura copiada al portapapeles")
                self.ui.show_message("✅ Estructura copiada al portapapeles", "success")
            else:
                self.ui.show_message("⚠️ No hay estructura para copiar", "warning")
        except Exception as e:
            self.logger.error(f"Error al copiar al portapapeles: {str(e)}")
            self.ui.show_message("❌ No se pudo copiar al portapapeles", "error")

    def guardar_estructura(self):
        """Guarda la estructura en un archivo"""
        try:
            estructura = self._get_preview_content()
            if not estructura:
                self.ui.show_message("⚠️ No hay estructura para guardar", "warning")
                return
                
            # Validar la estructura antes de guardar
            if not self._validate_preview_content():
                response = messagebox.askyesno(
                    "Advertencia",
                    "La estructura actual no tiene el formato correcto.\n\n" +
                    "¿Deseas guardarla de todos modos?\n" +
                    "(Se recomienda usar los símbolos └── y ├── para un formato válido)"
                )
                if not response:
                    return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[
                    ("Archivo Markdown", "*.md"),
                    ("Archivo de texto", "*.txt"),
                    ("Todos los archivos", "*.*")
                ],
                title="Guardar Estructura"
            )
            
            if filename:
                FileHandler.guardar_estructura(filename, estructura, self.usar_iconos.get())
                self.logger.info(f"Estructura guardada en: {filename}")
                self.ui.show_message(f"✅ Estructura guardada en {filename}", "success")
                
        except Exception as e:
            self.logger.error(f"Error al guardar estructura: {str(e)}")
            self.ui.show_message(f"❌ Error al guardar la estructura: {str(e)}", "error")

    def run(self):
        """Inicia la aplicación"""
        self.logger.info("Iniciando aplicación")
        
        # Obtener dimensiones de la pantalla y la ventana
        window_size = self.settings.get('window_size', '1000x700')
        window_width = int(window_size.split('x')[0])
        window_height = int(window_size.split('x')[1])
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Centrar la ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Mostrar mensaje inicial
        self.window.after(500, lambda: self.ui.show_message(
            "👋 ¡Bienvenido! Carga un directorio o pega una estructura para comenzar",
            "info",
            5000
        ))
        
        # Guardar preferencias al cerrar
        def on_closing():
            self.settings.set('usar_iconos', self.usar_iconos.get())
            self.settings.set('window_size', self.window.geometry().split('+')[0])
            self.settings.save_settings()
            self.window.destroy()
            
        self.window.protocol("WM_DELETE_WINDOW", on_closing)
        self.window.mainloop()
