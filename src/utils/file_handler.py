from pathlib import Path
import re
from datetime import datetime
import logging

logger = logging.getLogger('ConvertidorDirectorios')

class FileHandler:
    @staticmethod
    def generar_estructura_iconos(dir_path: str, level: int = 0, exclude_patterns=None) -> str:
        """Genera estructura con iconos"""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules']
            
        result = []
        try:
            base_path = Path(dir_path)
            if not any(base_path.iterdir()):
                return "📂 Directorio vacío"
                
            items = sorted(
                [item for item in base_path.iterdir() 
                 if not any(pattern in str(item) for pattern in exclude_patterns)],
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            
            for item in items:
                indent = "  " * level
                if item.is_file():
                    icon = FileHandler._get_file_icon(item.suffix)
                    result.append(f"{indent}{icon} {item.name}")
                elif item.is_dir():
                    result.append(f"{indent}📁 {item.name}/")
                    subdir_content = FileHandler.generar_estructura_iconos(
                        item, level + 1, exclude_patterns
                    )
                    if subdir_content:
                        result.append(subdir_content)
                        
            return "\n".join(result)
        except Exception as e:
            logger.error(f"Error generando estructura con iconos: {str(e)}")
            raise

    @staticmethod
    def generar_estructura_arbol(dir_path: str, level: int = 0, prefix="", exclude_patterns=None) -> str:
        """Genera estructura estilo árbol"""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules']
            
        result = []
        try:
            base_path = Path(dir_path)
            if not any(base_path.iterdir()):
                return "└── Directorio vacío"
                
            items = sorted(
                [item for item in base_path.iterdir() 
                 if not any(pattern in str(item) for pattern in exclude_patterns)],
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                indent = prefix + ("└── " if is_last else "├── ")
                
                if item.is_file():
                    result.append(f"{indent}{item.name}")
                elif item.is_dir():
                    result.append(f"{indent}{item.name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    subdir_content = FileHandler.generar_estructura_arbol(
                        item, level + 1, new_prefix, exclude_patterns
                    )
                    if subdir_content:
                        result.append(subdir_content)
                        
            return "\n".join(result)
        except Exception as e:
            logger.error(f"Error generando estructura árbol: {str(e)}")
            raise

    @staticmethod
    def validar_estructura_markdown(estructura: str) -> bool:
        """Valida que la estructura esté en formato markdown válido"""
        lineas = estructura.split('\n')
        nivel_actual = 0
        patron_arbol = r'^(\s*)(├──|└──|│\s+)?\s*(.+?)/?$'
        
        for linea in lineas:
            if not linea.strip():
                continue
                
            if not re.match(patron_arbol, linea):
                return False
                
            # Validar la indentación y símbolos
            espacios = len(re.match(r'^\s*', linea).group())
            if espacios % 4 != 0:
                return False
                
            nuevo_nivel = espacios // 4
            if nuevo_nivel > nivel_actual + 1:
                return False
                
            nivel_actual = nuevo_nivel
            
        return True

    @staticmethod
    def crear_estructura(estructura: str, base_path: str, usar_iconos: bool):
        """
        Crea la estructura de directorios a partir del markdown
        """
        if not estructura.strip():
            raise ValueError("La estructura está vacía")
            
        if not FileHandler.validar_estructura_markdown(estructura):
            raise ValueError("La estructura no está en formato markdown válido")
            
        try:
            lineas = [l for l in estructura.split('\n') if l.strip()]
            base_path = Path(base_path)
            nivel_actual = 0
            estructura_actual = {'path': base_path, 'children': {}}
            path_stack = [estructura_actual]
            
            for linea in lineas:
                # Obtener nivel de indentación
                espacios = len(re.match(r'^\s*', linea).group())
                nivel = espacios // 4
                
                # Obtener nombre y tipo (archivo/directorio)
                match = re.search(r'[├└]──\s*(.+?)/?$', linea)
                if not match:
                    continue
                    
                nombre = match.group(1).strip()
                es_directorio = nombre.endswith('/')
                nombre = nombre.rstrip('/')
                
                # Ajustar la pila según el nivel
                while len(path_stack) > nivel + 1:
                    path_stack.pop()
                
                # Crear el path completo
                parent = path_stack[-1]
                current_path = parent['path'] / nombre
                
                if es_directorio:
                    # Crear directorio
                    current_path.mkdir(parents=True, exist_ok=True)
                    nuevo_dir = {'path': current_path, 'children': {}}
                    parent['children'][nombre] = nuevo_dir
                    path_stack.append(nuevo_dir)
                    logger.info(f"Creado directorio: {current_path}")
                else:
                    # Crear archivo
                    current_path.parent.mkdir(parents=True, exist_ok=True)
                    current_path.touch()
                    parent['children'][nombre] = {'path': current_path}
                    logger.info(f"Creado archivo: {current_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al crear estructura: {str(e)}")
            raise

    @staticmethod
    def guardar_estructura(filename: str, estructura: str, usar_iconos: bool):
        """Guarda la estructura en un archivo"""
        try:
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            encabezado = f"""# Estructura de Directorios
            Generado por: ConvertidorDirectorios
            Fecha: {fecha_actual}
            Modo: {"Iconos" if usar_iconos else "Árbol"}

            ```
            {estructura}
            ```
            """
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(encabezado)
                
        except Exception as e:
            logger.error(f"Error al guardar estructura: {str(e)}")
            raise

    @staticmethod
    def _get_file_icon(extension: str) -> str:
        """Retorna el icono apropiado según la extensión del archivo"""
        extension = extension.lower()
        icons = {
        # Documentos
        '.txt': '📝',
        '.doc': '📘',
        '.docx': '📘',
        '.pdf': '📕',
        '.md': '📋',
        
        # Código
        '.py': '🐍',
        '.js': '📜',
        '.html': '🌐',
        '.css': '🎨',
        '.json': '📦',
        '.xml': '📦',
        '.dart': '💠',
        '.java': '☕',
        '.cpp': '⚡',
        '.c': '⚡',
        '.php': '🐘',
        '.rb': '💎',        # Ruby
        '.swift': '🕊️',    # Swift
        '.ts': '📘',        # TypeScript
        '.go': '🐹',        # Go
        '.rs': '🦀',        # Rust
        '.kt': '🔷',        # Kotlin
        '.sql': '🗃️',       # SQL
        
        # Imágenes
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.gif': '🖼️',
        '.svg': '🖼️',
        
        # Otros
        '.zip': '📦',
        '.rar': '📦',
        '.7z': '📦',
        '.exe': '⚙️',
        '.bat': '⚙️',
        '.sh': '⚙️',
        '.mp3': '🎵',
        '.wav': '🎵',
        '.mp4': '🎥',
        '.avi': '🎥',
        '.gitignore': '📋',
        '.env': '🔒',
        
        # Configuración y misceláneos
        '.yml': '⚙️',       # YAML config
        '.yaml': '⚙️',
        '.ini': '⚙️',       # Configuración
        '.log': '🗒️',       # Logs
        '.db': '🗄️'         # Bases de datos
    }
        
        return icons.get(extension, '📄')
