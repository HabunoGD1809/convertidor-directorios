import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class PreferencesDialog:
    def __init__(self, parent, settings, styles, apply_callback):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Preferencias")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        
        self.settings = settings
        self.styles = styles
        self.apply_callback = apply_callback
        
        # Hacer la ventana modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Valores actuales
        self.theme_var = tk.StringVar(value=settings.get('theme'))
        self.font_family_var = tk.StringVar(value=settings.get('font_family'))
        self.font_size_var = tk.StringVar(value=str(settings.get('font_size')))
        self.ui_font_family_var = tk.StringVar(value=settings.get('ui_font_family'))
        self.ui_font_size_var = tk.StringVar(value=str(settings.get('ui_font_size')))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        style = ttk.Style()
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sección de Tema
        self._create_section_label(main_frame, "Tema")
        theme_frame = ttk.Frame(main_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(
            theme_frame,
            text="Tema Oscuro",
            value="dark",
            variable=self.theme_var
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            theme_frame,
            text="Tema Claro",
            value="light",
            variable=self.theme_var
        ).pack(side=tk.LEFT, padx=5)
        
        # Sección de Fuente de Vista Previa
        self._create_section_label(main_frame, "Fuente de Vista Previa")
        
        # Familia de fuente
        font_family_frame = ttk.Frame(main_frame)
        font_family_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            font_family_frame,
            text="Familia:"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        font_families = sorted(list(set(tkfont.families())))
        font_combo = ttk.Combobox(
            font_family_frame,
            textvariable=self.font_family_var,
            values=font_families,
            state="readonly"
        )
        font_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tamaño de fuente
        font_size_frame = ttk.Frame(main_frame)
        font_size_frame.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(
            font_size_frame,
            text="Tamaño:"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        font_sizes = [str(i) for i in range(8, 25)]
        size_combo = ttk.Combobox(
            font_size_frame,
            textvariable=self.font_size_var,
            values=font_sizes,
            state="readonly",
            width=5
        )
        size_combo.pack(side=tk.LEFT)
        
        # Sección de Fuente de Interfaz
        self._create_section_label(main_frame, "Fuente de Interfaz")
        
        # Familia de fuente UI
        ui_font_family_frame = ttk.Frame(main_frame)
        ui_font_family_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            ui_font_family_frame,
            text="Familia:"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ui_font_combo = ttk.Combobox(
            ui_font_family_frame,
            textvariable=self.ui_font_family_var,
            values=font_families,
            state="readonly"
        )
        ui_font_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tamaño de fuente UI
        ui_font_size_frame = ttk.Frame(main_frame)
        ui_font_size_frame.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(
            ui_font_size_frame,
            text="Tamaño:"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ui_size_combo = ttk.Combobox(
            ui_font_size_frame,
            textvariable=self.ui_font_size_var,
            values=font_sizes,
            state="readonly",
            width=5
        )
        ui_size_combo.pack(side=tk.LEFT)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Aplicar",
            command=self._apply_changes
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _create_section_label(self, parent, text):
        """Crea una etiqueta de sección"""
        ttk.Label(
            parent,
            text=text,
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor=tk.W, pady=(0, 5))

    def _apply_changes(self):
        """Aplica los cambios de preferencias"""
        # Actualizar configuraciones
        self.settings.set('theme', self.theme_var.get())
        self.settings.set('font_family', self.font_family_var.get())
        self.settings.set('font_size', int(self.font_size_var.get()))
        self.settings.set('ui_font_family', self.ui_font_family_var.get())
        self.settings.set('ui_font_size', int(self.ui_font_size_var.get()))
        
        # Guardar y aplicar cambios
        self.settings.save_settings()
        self.apply_callback()
        
        # Cerrar diálogo
        self.dialog.destroy()
