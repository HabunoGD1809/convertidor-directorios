from pathlib import Path
import re
from datetime import datetime
import logging

logger = logging.getLogger('ConvertidorDirectorios')

class FileHandler:
    @staticmethod
    def _normalize_directory_structure(estructura: str) -> str:
        """Normaliza una estructura de directorios a un formato válido"""
        try:
            # Dividir en líneas y eliminar líneas vacías
            lines = [line.rstrip() for line in estructura.split('\n') if line.strip()]
            normalized_lines = []
            
            # Detectar el patrón de indentación usado
            indent_pattern = None
            for line in lines[1:]:  # Empezar desde la segunda línea
                spaces = len(line) - len(line.lstrip())
                if spaces > 0:
                    indent_pattern = spaces
                    break
            
            if not indent_pattern:
                indent_pattern = 2  # Valor por defecto si no se detecta
                
            # Procesar cada línea
            for i, line in enumerate(lines):
                # Calcular nivel actual
                spaces_before = len(line) - len(line.lstrip())
                current_level = spaces_before // indent_pattern if indent_pattern else 0
                
                # Limpiar la línea de símbolos existentes
                clean_line = line.lstrip()
                for symbol in ['├──', '└──', '│', '─', '├─', '└─', '|']:
                    clean_line = clean_line.replace(symbol, '')
                clean_line = clean_line.strip()
                
                # Determinar si es el último elemento en su nivel
                is_last = True
                for next_line in lines[i + 1:]:
                    next_spaces = len(next_line) - len(next_line.lstrip())
                    next_level = next_spaces // indent_pattern if indent_pattern else 0
                    if next_level <= current_level:
                        is_last = next_level < current_level
                        break
                
                # Construir la nueva línea
                new_line = ''
                
                # Agregar los conectores verticales para niveles anteriores
                for level in range(current_level):
                    # Verificar si hay más elementos en este nivel
                    has_more = False
                    for next_line in lines[i + 1:]:
                        next_spaces = len(next_line) - len(next_line.lstrip())
                        next_level = next_spaces // indent_pattern if indent_pattern else 0
                        if next_level > level:
                            has_more = True
                            break
                        elif next_level <= level:
                            break
                    new_line += '│   ' if has_more else '    '
                
                # Agregar el conector apropiado para el nivel actual
                new_line += '└── ' if is_last else '├── '
                new_line += clean_line
                
                normalized_lines.append(new_line)
            
            return '\n'.join(normalized_lines)
            
        except Exception as e:
            logger.error(f"Error normalizando estructura: {str(e)}")
            raise

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
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    subdir_content = FileHandler.generar_estructura_arbol(
                        item, level + 1, next_prefix, exclude_patterns
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
        try:
            # Si la estructura está vacía, no es válida
            if not estructura.strip():
                return False

            lineas = [l for l in estructura.split('\n') if l.strip()]
            niveles_validos = set()
            nivel_anterior = 0
            
            for linea in lineas:
                # Calcular nivel basado en la indentación
                indentacion = len(re.match(r'^\s*', linea).group())
                nivel = indentacion // 2  # Cambiado de 4 a 2 para ser más flexible
                
                # Registrar el nivel como válido
                niveles_validos.add(nivel)
                
                # Permitir cualquier nivel en la primera línea
                if len(niveles_validos) == 1:
                    nivel_anterior = nivel
                    continue
                
                # Verificar si hay símbolos de estructura
                tiene_simbolos = bool(re.search(r'[├└][-─]', linea))
                
                # Si la línea no tiene símbolos pero tiene contenido, tratarla como contenido válido
                if not tiene_simbolos and linea.strip():
                    continue
                
                # La diferencia de nivel no debería ser mayor que la profundidad máxima actual
                if nivel > max(niveles_validos) + 1:
                    return False
                
                nivel_anterior = nivel
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando estructura: {str(e)}")
            return False
        
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
