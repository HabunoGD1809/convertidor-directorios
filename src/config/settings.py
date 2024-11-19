import json
import os
from datetime import datetime

class Settings:
    def __init__(self):
        self.config_file = 'preferencias.json'
        self.default_settings = {
            'usar_iconos': True,
            'theme': 'dark',  # 'dark' o 'light'
            'font_family': 'Consolas',  # Fuente para el área de preview
            'font_size': 11,  # Tamaño de fuente para el preview
            'ui_font_family': 'Segoe UI',  # Fuente para la UI
            'ui_font_size': 10,  # Tamaño de fuente para la UI
            'window_size': '1000x700',
            'ultima_actualizacion': datetime.now().isoformat()
        }
        self.current_settings = {}
        self.load_settings()
        
    def load_settings(self):
        """Carga las preferencias desde el archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Combinar configuraciones guardadas con las predeterminadas
                    self.current_settings = {**self.default_settings, **saved_settings}
            else:
                self.current_settings = self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_settings = self.default_settings.copy()

    def save_settings(self):
        """Guarda las preferencias en el archivo JSON"""
        try:
            self.current_settings['ultima_actualizacion'] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Obtiene un valor de configuración"""
        return self.current_settings.get(key, self.default_settings.get(key, default))

    def set(self, key, value):
        """Establece un valor de configuración"""
        self.current_settings[key] = value
