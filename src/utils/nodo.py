from __future__ import annotations

import re
from pathlib import Path
import logging

logger = logging.getLogger('ConvertidorDirectorios')

class Nodo:
    """Representa un nodo (archivo o directorio) en la estructura del árbol."""
    def __init__(self, nombre: str, es_directorio: bool = False, nivel: int = 0):
        self.nombre: str = nombre
        self.es_directorio: bool = es_directorio
        self.hijos: list[Nodo] = []
        self.nivel: int = nivel
        self.padre: Nodo | None = None

    def agregar_hijo(self, hijo: Nodo):
        """Agrega un nodo hijo."""
        hijo.padre = self
        self.hijos.append(hijo)

    def __repr__(self):
        """Representación de cadena para depuración."""
        tipo = "Dir" if self.es_directorio else "File"
        return f"<Nodo(N:{self.nivel}, T:{tipo}, Nom:'{self.nombre}', H:{len(self.hijos)})>"

    @staticmethod
    def _parse_linea(linea: str) -> tuple[int, str, bool] | None:
        """
        Parsea una línea de la estructura para obtener nivel, nombre y tipo.
        Retorna (nivel, nombre, es_directorio) o None si no es válida.
        """
        linea = linea.rstrip()
        match = re.match(r'^([│\s]*(?:[├└]──\s*))?(.*)', linea)
        if not match:
             # Check if it's a root node (no prefix)
             if re.match(r'^[📁📄]?\s*[^│├└]+', linea.lstrip()):
                  nombre_limpio = linea.lstrip()
                  es_directorio = nombre_limpio.endswith('/') or nombre_limpio.startswith('📁')
                  nombre_limpio = nombre_limpio.rstrip('/').lstrip('📁📄 ').strip()
                  # Ensure name is not empty after stripping icons etc.
                  return (0, nombre_limpio, es_directorio) if nombre_limpio else None
             return None # Not a recognized format

        prefijo_simbolo = match.group(1) or ''
        nombre_linea = match.group(2).strip()
        prefijo_solo = re.match(r'^([│\s]*)', prefijo_simbolo).group(1) or ''
        # Calculate level based on visual structure (more robust than just spaces)
        nivel = prefijo_solo.count('│') + prefijo_solo.count('   ') # Count pipes and 3-space groups
        # Fallback or adjustment if using pure spaces (e.g., 4 spaces per level)
        if nivel == 0 and prefijo_solo.startswith('    '):
            nivel = len(prefijo_solo) // 4


        nombre_limpio = nombre_linea
        es_directorio = nombre_limpio.endswith('/')
        # Deduce type from icon if present and '/' is missing
        if nombre_limpio.startswith(('📁 ', '📄 ')):
            icon = nombre_limpio[:2]
            nombre_limpio = nombre_limpio[2:]
            if not es_directorio: # Only override if '/' is not present
                 es_directorio = icon == '📁 '

        nombre_limpio = nombre_limpio.rstrip('/') # Remove trailing slash if dir
        nombre_limpio = nombre_limpio.strip() # Clean extra whitespace

        if not nombre_limpio:
            logger.warning(f"Línea parseada sin nombre: '{linea}' -> Prefijo: '{prefijo_simbolo}', Nombre Línea: '{nombre_linea}'")
            return None # Ignore lines that result in an empty name

        return nivel, nombre_limpio, es_directorio


    @staticmethod
    def crear_desde_texto(estructura: str, base_path_str: str) -> Nodo | None:
        """
        Crea la estructura de directorios física a partir del texto.
        Retorna el nodo raíz lógico de la estructura creada o None si falla.
        """
        if not estructura.strip():
            raise ValueError("La estructura de texto para crear está vacía.")

        base_path = Path(base_path_str)
        if not base_path.is_dir():
             # Option: Create base_path if it doesn't exist? Or raise error?
             # Let's raise error for now, assuming user selected existing base.
             logger.error(f"El directorio base para la creación no existe: {base_path}")
             raise FileNotFoundError(f"El directorio base seleccionado no existe: {base_path_str}")

        lineas = [l for l in estructura.split('\n') if l.strip()]
        # Root node represents the base_path selected by the user
        raiz = Nodo(base_path.name, es_directorio=True, nivel=-1)
        ultimo_nodo_por_nivel = {-1: raiz} # Tracks the last node created at each level
        logger.info(f"Iniciando creación de estructura DENTRO de: {base_path}")

        try:
            for i, linea in enumerate(lineas):
                parsed = Nodo._parse_linea(linea)
                if not parsed:
                    logger.warning(f"Línea ignorada (formato no reconocido): {i+1} -> '{linea}'")
                    continue

                nivel, nombre, es_directorio = parsed
                logger.debug(f"Parseado L{i+1}: Nivel={nivel}, Nombre='{nombre}', Dir={es_directorio}")

                # Find the correct parent node based on level
                nivel_padre = nivel - 1
                while nivel_padre not in ultimo_nodo_por_nivel and nivel_padre >= -1:
                    # If exact parent level doesn't exist, go up until a valid parent is found
                    nivel_padre -= 1

                if nivel_padre < -1:
                     # This shouldn't happen if level 0 is parsed correctly relative to root (-1)
                     logger.error(f"No se pudo encontrar un nodo padre válido para la línea {i+1} (Nivel {nivel}): '{linea}'. Saltando.")
                     continue

                padre = ultimo_nodo_por_nivel[nivel_padre]

                # Create the new node object
                nuevo_nodo = Nodo(nombre, es_directorio, nivel)
                padre.agregar_hijo(nuevo_nodo)
                # Register this node as the last one created at its level
                ultimo_nodo_por_nivel[nivel] = nuevo_nodo

                # Determine the actual file system path for the new node
                # Build path relative to the base_path by joining names from root
                ruta_relativa_parts = [n.nombre for n in nuevo_nodo.ruta_desde(raiz)[1:]] # Get names excluding logical root
                ruta_nodo_absoluta = base_path.joinpath(*ruta_relativa_parts) # Join parts to the actual base path

                logger.debug(f"  -> Creando item físico: {ruta_nodo_absoluta} (Padre lógico: {padre.nombre} @ Nivel {padre.nivel})")

                # Create the directory or file on the filesystem
                try:
                     if es_directorio:
                         ruta_nodo_absoluta.mkdir(parents=True, exist_ok=True)
                     else:
                         # Ensure parent directory exists first
                         ruta_nodo_absoluta.parent.mkdir(parents=True, exist_ok=True)
                         # Create empty file
                         ruta_nodo_absoluta.touch(exist_ok=True)
                except PermissionError as pe:
                     logger.error(f"Permiso denegado al crear item físico: {ruta_nodo_absoluta}. Error: {pe}")
                     # Stop creation process on critical errors like permissions
                     raise
                except Exception as fs_error:
                     logger.error(f"Error del sistema de archivos al crear {ruta_nodo_absoluta}: {fs_error}", exc_info=True)
                     # Stop creation process on other filesystem errors
                     raise

            logger.info(f"Creación de estructura física completada dentro de {base_path}.")
            return raiz # Return the logical root node representing the created structure

        except Exception as e:
            # Catch any exception during the loop (like re-raised PermissionError)
            logger.error(f"Error fatal durante la creación desde texto: {str(e)}", exc_info=True)
            # Indicate failure by returning None
            return None


    def ruta_desde(self, ancestro: Nodo) -> list[Nodo]:
        """Retorna la lista de nodos desde el ancestro especificado hasta este nodo."""
        ruta = []
        nodo_actual: Nodo | None = self
        while nodo_actual and nodo_actual != ancestro:
            ruta.append(nodo_actual)
            nodo_actual = nodo_actual.padre # Move up to the parent
        # Include ancestor if found
        if nodo_actual == ancestro:
             ruta.append(ancestro)
        # If ancestor was not found (e.g., different trees), path will be from self up to root
        # Return reversed list so it's from ancestor -> self
        return ruta[::-1]
