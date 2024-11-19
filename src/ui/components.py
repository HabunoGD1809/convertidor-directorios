import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import pyperclip

class UIComponents:
    def __init__(self, parent, styles, callbacks):
        self.parent = parent
        self.styles = styles
        self.callbacks = callbacks
        self.message_label = None
        self.preview_placeholder = 'Pega aquí tu estructura o carga un directorio...'
        
    def create_title_section(self):
        """Crea la sección del título"""
        titulo_frame = ttk.Frame(self.parent, style='TFrame')
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para el título y botón de preferencias
        header_frame = ttk.Frame(titulo_frame, style='TFrame')
        header_frame.pack(fill=tk.X)
        
        # Logo o icono (puedes agregar uno si lo deseas)
        titulo = ttk.Label(
            header_frame,
            text="🌳 Convertidor de Estructuras de Directorios",
            style='Title.TLabel'
        )
        titulo.pack(side=tk.LEFT, pady=10)
        
        # Frame para botones de la derecha
        right_buttons = ttk.Frame(header_frame, style='TFrame')
        right_buttons.pack(side=tk.RIGHT, pady=10)
        
        # Botón de tema
        theme_button = ttk.Button(
            right_buttons,
            text="🎨 Tema",
            style='Custom.TButton',
            command=self.callbacks['abrir_preferencias']
        )
        theme_button.pack(side=tk.RIGHT, padx=5)
        
        return titulo_frame

    def create_options_section(self, usar_iconos_var):
        """Crea la sección de opciones"""
        opciones_frame = ttk.LabelFrame(
            self.parent,
            text="🛠️ Opciones",
            padding="10",
            style='TLabelframe'
        )
        opciones_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame izquierdo para el checkbox
        left_frame = ttk.Frame(opciones_frame, style='TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        checkbox = ttk.Checkbutton(
            left_frame,
            text="Usar iconos en la estructura",
            variable=usar_iconos_var,
            command=self.callbacks['actualizar_preview'],
            style='TCheckbutton'
        )
        checkbox.pack(side=tk.LEFT, padx=5)
        
        # Tooltip o ayuda
        ttk.Label(
            left_frame,
            text="💡 Los iconos hacen la estructura más visual",
            style='Custom.TLabel'
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        return opciones_frame

    def create_buttons_section(self):
        """Crea la sección de botones principales"""
        botones_frame = ttk.Frame(self.parent, style='TFrame')
        botones_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales con descripciones
        buttons_config = [
            {
                "text": "📂 Cargar Directorio",
                "command": self.callbacks['convertir_directorio'],
                "desc": "Selecciona una carpeta para convertir su estructura"
            },
            {
                "text": "🔨 Crear Estructura",
                "command": self.callbacks['crear_desde_estructura'],
                "desc": "Crea directorios a partir de la estructura del editor"
            }
        ]
        
        for btn_config in buttons_config:
            btn_frame = ttk.Frame(botones_frame, style='TFrame')
            btn_frame.pack(side=tk.LEFT, padx=5)
            
            btn = ttk.Button(
                btn_frame,
                text=btn_config["text"],
                style='Custom.TButton',
                command=btn_config["command"]
            )
            btn.pack(anchor=tk.W)
            
            desc_label = ttk.Label(
                btn_frame,
                text=btn_config["desc"],
                style='Custom.TLabel',
                font=('Segoe UI', 8)
            )
            desc_label.pack(anchor=tk.W)
        
        return botones_frame

# dfdsfdf
    def create_preview_section(self):
        """Crea la sección de vista previa/editor"""
        preview_container = ttk.LabelFrame(
            self.parent,
            text="📝 Editor de Estructura",
            padding="10",
            style='TLabelframe'
        )
        preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Panel de instrucciones
        instructions_frame = ttk.Frame(preview_container, style='TFrame')
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions = [
            "💡 Aquí puedes:",
            "  • Ver la estructura generada desde un directorio",
            "  • Pegar una estructura existente en formato markdown",
            "  • Editar manualmente la estructura usando los botones de abajo",
            "  • Usar espacios (4 espacios o 1 tab) para indicar niveles"
        ]
        
        for inst in instructions:
            ttk.Label(
                instructions_frame,
                text=inst,
                style='Custom.TLabel'
            ).pack(anchor=tk.W)
        
        # Frame para mensajes
        self.message_frame = ttk.Frame(preview_container, style='TFrame')
        self.message_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Área de texto con frame personalizado
        text_frame = ttk.Frame(preview_container, style='Preview.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de herramientas mejorada
        toolbar = ttk.Frame(text_frame, style='TFrame')
        toolbar.pack(fill=tk.X, padx=1, pady=1)
        
        # Frame para los botones de símbolos con etiqueta
        symbols_frame = ttk.LabelFrame(toolbar, text="Insertar Símbolos", style='TLabelframe')
        symbols_frame.pack(fill=tk.X, padx=5, pady=5)
        
        toolbar_buttons = [
            ("└── Último", "Insertar símbolo de último elemento", "    └── "),
            ("├── Elemento", "Insertar símbolo de elemento", "    ├── "),
            ("│   Línea", "Insertar línea vertical", "    │   "),
            ("↹ Tab", "Insertar indentación (4 espacios)", "    ")
        ]
        
        for text, tooltip, symbol in toolbar_buttons:
            btn = ttk.Button(
                symbols_frame,
                text=text,
                style='Custom.TButton',
                width=12
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            btn.configure(command=lambda s=symbol: self._insert_symbol(s))
            self._create_tooltip(btn, tooltip)
        
        # Área de texto
        preview_text = tk.Text(
            text_frame,
            **self.styles.get_text_widget_config()
        )
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=preview_text.yview)
        x_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=preview_text.xview)
        preview_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Empaquetar elementos
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar placeholder
        preview_text.insert('1.0', self.preview_placeholder)
        preview_text.configure(fg='gray')
        
        def on_focus_in(event):
            if preview_text.get('1.0', 'end-1c') == self.preview_placeholder:
                preview_text.delete('1.0', tk.END)
                preview_text.configure(fg=self.styles.current_theme['preview_fg'])
                
            # Verificar portapapeles
            try:
                from src.utils.file_handler import FileHandler
                clipboard_content = self.parent.clipboard_get()
                if clipboard_content and FileHandler.validar_estructura_markdown(clipboard_content):
                    self.show_message(
                        "📋 Detectado contenido válido en el portapapeles. " +
                        "Usa Ctrl+V o clic derecho > Pegar para usarlo",
                        "info",
                        5000
                    )
            except Exception:
                pass
        
        def on_focus_out(event):
            if not preview_text.get('1.0', 'end-1c').strip():
                preview_text.configure(fg='gray')
                preview_text.insert('1.0', self.preview_placeholder)
        
        def on_key_release(event):
            # Validar estructura cuando el usuario escribe
            try:
                from src.utils.file_handler import FileHandler
                content = preview_text.get('1.0', 'end-1c').strip()
                if content and content != self.preview_placeholder:
                    if not FileHandler.validar_estructura_markdown(content):
                        self.show_message(
                            "⚠️ La estructura actual no es válida. Usa los botones de símbolos para un formato correcto.",
                            "warning"
                        )
            except Exception:
                pass
        
        preview_text.bind('<FocusIn>', on_focus_in)
        preview_text.bind('<FocusOut>', on_focus_out)
        preview_text.bind('<KeyRelease>', on_key_release)
        
        # Crear menú contextual mejorado
        self._create_context_menu(preview_text)
        
        return preview_container, preview_text

    def _insert_symbol(self, symbol):
        """Inserta un símbolo en la posición actual del cursor"""
        if hasattr(self, 'preview_text'):
            if self.preview_text.get('1.0', 'end-1c') == self.preview_placeholder:
                self.preview_text.delete('1.0', tk.END)
                self.preview_text.configure(fg=self.styles.current_theme['preview_fg'])
            
            # Obtener posición actual y línea
            cursor_pos = self.preview_text.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            
            # Si no estamos al inicio de la línea y no hay un salto de línea antes,
            # agregar un salto de línea
            if self.preview_text.get(line_start, cursor_pos).strip():
                symbol = '\n' + symbol
            
            self.preview_text.insert(tk.INSERT, symbol)
            self.preview_text.focus_set()  # Mantener el foco en el área de texto

    def _create_context_menu(self, text_widget):
        """Crea un menú contextual mejorado para el widget de texto"""
        menu = tk.Menu(self.parent, tearoff=0)
        
        menu.add_command(label="📋 Copiar", command=lambda: text_widget.event_generate("<<Copy>>"))
        menu.add_command(label="📋 Pegar", command=lambda: self._paste_with_validation(text_widget))
        menu.add_command(label="✂️ Cortar", command=lambda: text_widget.event_generate("<<Cut>>"))
        menu.add_separator()
        menu.add_command(label="Seleccionar Todo", command=lambda: text_widget.tag_add("sel", "1.0", "end"))
        menu.add_separator()
        
        # Submenú para insertar símbolos
        symbols_menu = tk.Menu(menu, tearoff=0)
        symbols_menu.add_command(label="└── Último elemento", 
                               command=lambda: self._insert_symbol("    └── "))
        symbols_menu.add_command(label="├── Elemento", 
                               command=lambda: self._insert_symbol("    ├── "))
        symbols_menu.add_command(label="│   Línea vertical", 
                               command=lambda: self._insert_symbol("    │   "))
        symbols_menu.add_command(label="    Indentación", 
                               command=lambda: self._insert_symbol("    "))
        menu.add_cascade(label="Insertar Símbolo", menu=symbols_menu)
        
        def show_menu(event):
            menu.post(event.x_root, event.y_root)
            
        text_widget.bind("<Button-3>", show_menu)  # Windows/Linux
        text_widget.bind("<Button-2>", show_menu)  # macOS

    def _paste_with_validation(self, text_widget):
        """Pega el contenido con validación"""
        try:
            from src.utils.file_handler import FileHandler
            clipboard_content = self.parent.clipboard_get()
            
            if clipboard_content:
                if FileHandler.validar_estructura_markdown(clipboard_content):
                    text_widget.event_generate("<<Paste>>")
                    self.show_message("✅ Estructura pegada correctamente", "success")
                else:
                    if text_widget.get('1.0', 'end-1c') == self.preview_placeholder:
                        text_widget.delete('1.0', tk.END)
                    text_widget.event_generate("<<Paste>>")
                    self.show_message(
                        "⚠️ La estructura pegada podría no ser válida. Revisa el formato.",
                        "warning"
                    )
        except Exception:
            text_widget.event_generate("<<Paste>>")
    # cambio no
    def _get_preview_content(self):
            """Obtiene el contenido real del preview, ignorando el placeholder"""
            if hasattr(self, 'preview_text'):
                content = self.preview_text.get("1.0", "end-1c").strip()
                if content == self.preview_placeholder:
                    return ""
                return content
            return ""

    def _validate_preview_content(self):
        """Valida el contenido actual del preview"""
        try:
            from src.utils.file_handler import FileHandler
            content = self._get_preview_content()
            if content:
                return FileHandler.validar_estructura_markdown(content)
        except Exception:
            pass
        return False
# dsfdfd
    def create_action_buttons(self):
        """Crea los botones de acción"""
        acciones_frame = ttk.Frame(self.parent, style='TFrame')
        acciones_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons_config = [
            ("📋 Copiar", self.callbacks['copiar_estructura'], "Copiar al portapapeles"),
            ("💾 Guardar", self.callbacks['guardar_estructura'], "Guardar en archivo")
        ]
        
        for texto, comando, tooltip in buttons_config:
            btn = ttk.Button(
                acciones_frame,
                text=texto,
                style='Custom.TButton',
                command=comando
            )
            btn.pack(side=tk.LEFT, padx=5)
            self._create_tooltip(btn, tooltip)
        
        return acciones_frame

    def create_footer(self):
        """Crea el pie de página"""
        footer_frame = ttk.Frame(self.parent, style='TFrame')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Versión a la izquierda
        version_label = ttk.Label(
            footer_frame,
            text="v1.0.0",
            style='Custom.TLabel'
        )
        version_label.pack(side=tk.LEFT)
        
        # Firma al centro
        firma = ttk.Label(
            footer_frame,
            text="Creado por HabunoGD1809",
            style='Custom.TLabel'
        )
        firma.pack(side=tk.RIGHT)
        
        return footer_frame

    def show_message(self, message, message_type='info', duration=3000):
        """Muestra un mensaje temporal"""
        # Limpiar mensaje anterior si existe
        if self.message_label:
            self.message_label.destroy()
            
        # Crear nuevo mensaje
        self.message_label = ttk.Label(
            self.message_frame,
            text=message,
            style=self.styles.get_message_style(message_type),
            wraplength=800
        )
        self.message_label.pack(fill=tk.X, pady=5)
        
        # Programar la eliminación del mensaje
        self.parent.after(duration, self._clear_message)
        
    def _clear_message(self):
        """Limpia el mensaje actual"""
        if self.message_label:
            self.message_label.destroy()
            self.message_label = None

    def _create_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Creates a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(
                self.tooltip,
                text=text,
                justify=tk.LEFT,
                background=self.styles.current_theme['bg_color'],
                foreground=self.styles.current_theme['fg_color'],
                relief='solid',
                borderwidth=1,
                padding=(5, 2)
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
