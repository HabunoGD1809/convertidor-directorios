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
        """Agrega un nodo hijo y se asegura que el nodo actual es un directorio."""
        # FIX: Si un nodo tiene hijos, DEBE ser un directorio.
        self.es_directorio = True
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
        match = re.match(r'^([│\s]*(?:[├└]──\s*)?)(.*)', linea)
        if not match:
            return None

        prefijo_completo = match.group(1) or ''
        nombre_linea = match.group(2)

        # Cálculo de nivel basado en la estructura visual
        indent_str = re.sub(r'[├└]──.*', '', prefijo_completo)
        nivel = indent_str.count('│') + indent_str.count('    ') + indent_str.count('   ')

        # Heurística inicial para el tipo (se corregirá después si tiene hijos)
        nombre_limpio = nombre_linea.strip()
        es_directorio = nombre_limpio.endswith('/')

        if nombre_limpio.startswith(('📁 ', '📄 ')):
            icon = nombre_limpio[:2]
            nombre_limpio = nombre_limpio[2:]
            if not es_directorio:
                 es_directorio = icon == '📁 '
        # Heurística: si no tiene extensión, es probable que sea un directorio.
        # Esto ayuda a manejar casos como 'config' sin una '/' al final.
        elif '.' not in Path(nombre_limpio).name:
            es_directorio = True
        
        # Un archivo puede no tener extensión, la lógica de 'agregar_hijo' lo corregirá si es necesario.
        # Si algo como 'main.dart' se marca como directorio, lo siguiente lo corregirá
        if '.' in Path(nombre_limpio).name and not nombre_limpio.endswith('/'):
            es_directorio = False

        nombre_limpio = nombre_limpio.rstrip('/').strip()

        if not nombre_limpio:
            logger.warning(f"Línea parseada sin nombre: '{linea}'")
            return None

        return nivel, nombre_limpio, es_directorio

    @staticmethod
    def crear_desde_texto(estructura: str, base_path_str: str) -> Nodo | None:
        """
        Crea la estructura de directorios física a partir del texto.
        FIX: Reelaborado en un proceso de dos pasadas para mayor robustez.
        """
        if not estructura.strip():
            raise ValueError("La estructura de texto para crear está vacía.")

        base_path = Path(base_path_str)
        if not base_path.is_dir():
             logger.error(f"El directorio base para la creación no existe: {base_path}")
             raise FileNotFoundError(f"El directorio base seleccionado no existe: {base_path_str}")

        # --- PASO 1: Construir el árbol lógico en memoria ---
        lineas = [l for l in estructura.split('\n') if l.strip()]
        raiz = Nodo(base_path.name, es_directorio=True, nivel=-1)
        ultimo_nodo_por_nivel = {-1: raiz}
        logger.info(f"Iniciando creación de estructura DENTRO de: {base_path}")
        logger.info("Paso 1: Construyendo árbol lógico...")

        for i, linea in enumerate(lineas):
            parsed = Nodo._parse_linea(linea)
            if not parsed:
                logger.warning(f"Línea ignorada (formato no reconocido): {i+1} -> '{linea}'")
                continue

            nivel, nombre, es_directorio = parsed
            logger.debug(f"Parseado L{i+1}: Nivel={nivel}, Nombre='{nombre}', Dir={es_directorio} (inicial)")

            nivel_padre = nivel - 1
            while nivel_padre not in ultimo_nodo_por_nivel and nivel_padre >= -1:
                nivel_padre -= 1

            if nivel_padre < -1:
                 logger.error(f"No se pudo encontrar un nodo padre válido para la línea {i+1} (Nivel {nivel}): '{linea}'. Saltando.")
                 continue

            padre = ultimo_nodo_por_nivel[nivel_padre]
            nuevo_nodo = Nodo(nombre, es_directorio, nivel)
            padre.agregar_hijo(nuevo_nodo) # Esto corrige el flag 'es_directorio' del padre si es necesario
            ultimo_nodo_por_nivel[nivel] = nuevo_nodo

        logger.info("Árbol lógico construido. Iniciando creación física.")

        # --- PASO 2: Recorrer el árbol lógico y crear la estructura física ---
        def crear_recursivo(nodo: Nodo, ruta_padre_fisico: Path):
            """Función anidada para crear archivos/directorios recursivamente."""
            # No procesar el nodo raíz, que representa el directorio base ya existente
            if nodo == raiz:
                for hijo in nodo.hijos:
                    crear_recursivo(hijo, ruta_padre_fisico)
                return

            ruta_actual = ruta_padre_fisico / nodo.nombre
            try:
                if nodo.es_directorio:
                    logger.debug(f"  -> Creando Directorio: {ruta_actual}")
                    ruta_actual.mkdir(exist_ok=True)
                    for hijo in nodo.hijos:
                        crear_recursivo(hijo, ruta_actual)
                else:
                    logger.debug(f"  -> Creando Archivo: {ruta_actual}")
                    # El directorio padre ya ha sido creado por la llamada recursiva anterior
                    ruta_actual.touch(exist_ok=True)
            except Exception as e:
                logger.error(f"Error del sistema de archivos al procesar {ruta_actual}: {e}", exc_info=True)
                raise # Re-lanzar para que el bloque principal lo capture

        try:
            crear_recursivo(raiz, base_path)
            logger.info(f"Creación de estructura física completada.")
            return raiz
        except Exception as e:
            # Captura errores durante la creación física recursiva
            logger.error(f"Error fatal durante la creación física desde texto: {str(e)}", exc_info=True)
            # Falla y retorna None
            return None

    def ruta_desde(self, ancestro: Nodo) -> list[Nodo]:
        """Retorna la lista de nodos desde el ancestro especificado hasta este nodo."""
        ruta = []
        nodo_actual: Nodo | None = self
        while nodo_actual and nodo_actual != ancestro:
            ruta.append(nodo_actual)
            nodo_actual = nodo_actual.padre
        if nodo_actual == ancestro:
             ruta.append(ancestro)
        return ruta[::-1]
