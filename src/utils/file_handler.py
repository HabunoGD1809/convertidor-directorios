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
                current_prefix = prefix + ("└── " if is_last else "├── ")
                    
                if item.is_file():
                    result.append(f"{current_prefix}{item.name}")
                elif item.is_dir():
                    result.append(f"{current_prefix}{item.name}/")
                    # Mejorar la consistencia del prefijo para subdirectorios
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    subdir_content = FileHandler.generar_estructura_arbol(
                        item, level + 1, next_prefix, exclude_patterns
                    )
                    if subdir_content:
                        # Asegurar que las líneas verticales se alineen correctamente
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
    
class Nodo:
    def __init__(self, nombre, es_directorio=False):
        self.nombre = nombre
        self.es_directorio = es_directorio
        self.hijos = []
        self.nivel = 0

    @staticmethod
    def crear_estructura(estructura: str, base_path: str, usar_iconos: bool):
        """
        Crea la estructura de directorios a partir del markdown
        """
        if not estructura.strip():
            raise ValueError("La estructura está vacía")
                
        try:
            lineas = [l for l in estructura.split('\n') if l.strip()]
            raiz = Nodo("root", True)
            ultimo_nodo = {-1: raiz}  # Diccionario de último nodo por nivel
            
            logger.info("Construyendo árbol de directorios...")
            
            for linea in lineas:
                # Calculo de nivel basado en la cantidad de caracteres de indentación
                # incluidos los caracteres especiales
                nivel = 0
                for char in linea:
                    if char in ['│', ' ']:
                        nivel += 1
                    else:
                        break
                nivel = nivel // 4  # Convertir a nivel real
                
                logger.info(f"Procesando línea: [{linea}]")
                logger.info(f"Nivel calculado: {nivel}")
                
                match = re.search(r'[├└]──\s*(.+?)$', linea)
                if not match:
                    logger.info(f"No se encontró patrón en la línea: [{linea}]")
                    continue
                    
                nombre = match.group(1).strip()
                es_directorio = nombre.endswith('/')
                nombre = nombre.rstrip('/')
                
                # Debug: mostrar información del nodo
                logger.info(f"Nombre extraído: [{nombre}]")
                logger.info(f"Es directorio: {es_directorio}")
                
                # Creacion de nuevo nodo
                nuevo_nodo = Nodo(nombre, es_directorio)
                nuevo_nodo.nivel = nivel
                
                # Encontrar el padre correcto para este nodo
                padre = ultimo_nodo.get(nivel - 1, raiz)
                padre.hijos.append(nuevo_nodo)
                ultimo_nodo[nivel] = nuevo_nodo
                
                logger.info(f"Nodo creado - Nivel: {nivel}, Nombre: {nombre}, " +
                        f"Es directorio: {es_directorio}, Padre: {padre.nombre}")
                logger.info("-" * 50)
            
            # Creacion de estructura física
            logger.info("Creando estructura física...")
            
            def crear_estructura_fisica(nodo, ruta_actual):
                ruta_nodo = ruta_actual / nodo.nombre
                
                if nodo.es_directorio:
                    logger.info(f"Creando directorio: {ruta_nodo}")
                    ruta_nodo.mkdir(parents=True, exist_ok=True)
                    
                    # Creacion de hijos
                    for hijo in nodo.hijos:
                        crear_estructura_fisica(hijo, ruta_nodo)
                else:
                    logger.info(f"Creando archivo: {ruta_nodo}")
                    ruta_nodo.parent.mkdir(parents=True, exist_ok=True)
                    ruta_nodo.touch()
            
            # Creacion de la estructura física empezando desde los hijos de la raíz
            base_path = Path(base_path)
            for hijo in raiz.hijos:
                crear_estructura_fisica(hijo, base_path)
            
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
