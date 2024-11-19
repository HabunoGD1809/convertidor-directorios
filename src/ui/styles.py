class Styles:
    THEMES = {
        'dark': {
            'bg_color': '#1e1e1e',
            'fg_color': '#ffffff',
            'text_bg': '#2d2d2d',
            'text_fg': '#e0e0e0',
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
            'select_bg': '#264f78',
            'border_color': '#404040',
            'hover_bg': '#4d4d4d',
            'preview_bg': '#2d2d2d',
            'preview_fg': '#e0e0e0',
            'title_fg': '#00a5ff',
            'error_color': '#ff6b6b',
            'success_color': '#4cd964',
            'warning_color': '#ffcd38'
        },
        'light': {
            'bg_color': '#f5f5f5',
            'fg_color': '#000000',
            'text_bg': '#ffffff',
            'text_fg': '#000000',
            'button_bg': '#e0e0e0',
            'button_fg': '#000000',
            'select_bg': '#b3d7ff',
            'border_color': '#cccccc',
            'hover_bg': '#d0d0d0',
            'preview_bg': '#ffffff',
            'preview_fg': '#000000',
            'title_fg': '#0066cc',
            'error_color': '#dc3545',
            'success_color': '#28a745',
            'warning_color': '#ffc107'
        }
    }
    
    def __init__(self, settings):
        self.settings = settings
        self.current_theme = self.THEMES[settings.get('theme', 'dark')]
    
    def configure_styles(self, style):
        """Configura los estilos de la interfaz"""
        theme_colors = self.current_theme
        ui_font = (
            self.settings.get('ui_font_family', 'Segoe UI'),
            self.settings.get('ui_font_size', 10)
        )
        title_font = (
            self.settings.get('ui_font_family', 'Segoe UI'),
            self.settings.get('ui_font_size', 10) + 6,
            'bold'
        )
        
        # Estilos generales
        style.configure('.',
            background=theme_colors['bg_color'],
            foreground=theme_colors['fg_color'],
            font=ui_font
        )
        
        # Botones
        style.configure('Custom.TButton',
            padding=5,
            font=ui_font,
            background=theme_colors['button_bg'],
            foreground=theme_colors['button_fg']
        )
        
        style.map('Custom.TButton',
            background=[('active', theme_colors['hover_bg'])]
        )
        
        # Etiquetas
        style.configure('Custom.TLabel',
            font=ui_font,
            background=theme_colors['bg_color'],
            foreground=theme_colors['fg_color']
        )
        
        style.configure('Title.TLabel',
            font=title_font,
            background=theme_colors['bg_color'],
            foreground=theme_colors['title_fg']
        )
        
        style.configure('Preview.TLabel',
            font=('Consolas', 11),
            background=theme_colors['preview_bg'],
            foreground=theme_colors['preview_fg']
        )
        
        # Frames y LabelFrames
        style.configure('TFrame',
            background=theme_colors['bg_color']
        )
        
        style.configure('TLabelframe',
            background=theme_colors['bg_color'],
            foreground=theme_colors['fg_color']
        )
        
        style.configure('TLabelframe.Label',
            background=theme_colors['bg_color'],
            foreground=theme_colors['fg_color'],
            font=ui_font
        )
        
        # Checkbutton
        style.configure('TCheckbutton',
            background=theme_colors['bg_color'],
            foreground=theme_colors['fg_color'],
            font=ui_font
        )
        
        # Preview Frame especial
        style.configure('Preview.TFrame',
            background=theme_colors['preview_bg'],
            borderwidth=1,
            relief='solid'
        )
        
        # Estilos para mensajes
        style.configure('Success.TLabel',
            foreground=theme_colors['success_color'],
            background=theme_colors['bg_color'],
            font=ui_font
        )
        
        style.configure('Error.TLabel',
            foreground=theme_colors['error_color'],
            background=theme_colors['bg_color'],
            font=ui_font
        )
        
        style.configure('Warning.TLabel',
            foreground=theme_colors['warning_color'],
            background=theme_colors['bg_color'],
            font=ui_font
        )

    def get_text_widget_config(self):
        """Retorna la configuración para el widget de texto"""
        theme_colors = self.current_theme
        return {
            'wrap': 'none',
            'font': (
                self.settings.get('font_family', 'Consolas'),
                self.settings.get('font_size', 11)
            ),
            'bg': theme_colors['preview_bg'],
            'fg': theme_colors['preview_fg'],
            'insertbackground': theme_colors['fg_color'],
            'selectbackground': theme_colors['select_bg'],
            'selectforeground': theme_colors['fg_color'],
            'relief': 'solid',
            'borderwidth': 1,
            'padx': 10,
            'pady': 10
        }
        
    def update_theme(self, theme_name):
        """Actualiza el tema actual"""
        self.current_theme = self.THEMES[theme_name]

    def get_message_style(self, message_type):
        """Retorna el estilo según el tipo de mensaje"""
        return {
            'success': 'Success.TLabel',
            'error': 'Error.TLabel',
            'warning': 'Warning.TLabel'
        }.get(message_type, 'Custom.TLabel')
