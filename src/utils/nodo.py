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
        Retorna (nivel, nombre, es_directorio) o None si no es válida o es comentario.
        """
        linea = linea.replace('\xa0', ' ').rstrip()
        
        # Ignorar comentarios quirúrgicamente desde la raíz del parsing
        if linea.lstrip().startswith('#'):
            return None

        match = re.match(r'^([│\s]*(?:[├└]──\s*)?)(.*)', linea)
        if not match:
            return None

        prefijo_completo = (match.group(1) or '').replace('\t', '    ')
        nombre_linea = match.group(2)

        # Eliminar comentarios en línea
        nombre_linea = re.sub(r'\s+#.*$', '', nombre_linea)

        # --- 1. NUEVO CÁLCULO DE NIVEL ROBUSTO ---
        # Contamos indicadores explícitos visuales
        nivel = prefijo_completo.count('│') + prefijo_completo.count('├') + prefijo_completo.count('└')
        
        # Los espacios puros también pueden ser niveles si el usuario usó tabulaciones o espacios sin pipes
        espacios_restantes = re.sub(r'[│├└]──\s*|│\s*', '', prefijo_completo)
        nivel += len(espacios_restantes) // 4
        # -----------------------------------------

        # --- 2. NUEVA LÓGICA ARCHIVO VS CARPETA ---
        nombre_limpio = nombre_linea.strip()
        es_directorio = nombre_limpio.endswith('/')

        if nombre_limpio.startswith(('📁 ', '📄 ')):
            icon = nombre_limpio[:2]
            nombre_limpio = nombre_limpio[2:]
            if not es_directorio: # Si no hay slash explícito, respetamos el icono
                 es_directorio = (icon == '📁 ')

        nombre_limpio = nombre_limpio.rstrip('/').strip()

        if not nombre_limpio:
            logger.warning(f"Línea parseada sin nombre: '{linea}'")
            return None
        
        return nivel, nombre_limpio, es_directorio

    @staticmethod
    def crear_desde_texto(estructura: str, base_path_str: str) -> Nodo | None:
        """
        Crea la estructura de directorios física a partir del texto.
        """
        if not estructura.strip():
            raise ValueError("La estructura de texto para crear está vacía.")

        base_path = Path(base_path_str)
        if not base_path.is_dir():
             logger.error(f"El directorio base para la creación no existe: {base_path}")
             raise FileNotFoundError(f"El directorio base seleccionado no existe: {base_path_str}")

        lineas = [l for l in estructura.split('\n') if l.strip()]
        raiz = Nodo(base_path.name, es_directorio=True, nivel=-1)
        ultimo_nodo_por_nivel = {-1: raiz}
        logger.info(f"Iniciando creación de estructura DENTRO de: {base_path}")

        for i, linea in enumerate(lineas):
            parsed = Nodo._parse_linea(linea)
            if not parsed:
                continue

            nivel, nombre, es_directorio = parsed

            # Buscar el padre adecuado basado en el nivel
            nivel_padre = nivel - 1
            while nivel_padre not in ultimo_nodo_por_nivel and nivel_padre >= -1:
                nivel_padre -= 1

            if nivel_padre < -1:
                 logger.error(f"No se pudo encontrar un nodo padre válido para la línea {i+1} (Nivel {nivel}): '{linea}'. Saltando.")
                 continue

            padre = ultimo_nodo_por_nivel[nivel_padre]
            nuevo_nodo = Nodo(nombre, es_directorio, nivel)
            padre.agregar_hijo(nuevo_nodo) 
            ultimo_nodo_por_nivel[nivel] = nuevo_nodo

        def crear_recursivo(nodo: Nodo, ruta_padre_fisico: Path):
            if nodo == raiz:
                for hijo in nodo.hijos:
                    crear_recursivo(hijo, ruta_padre_fisico)
                return

            ruta_actual = ruta_padre_fisico / nodo.nombre
            try:
                if nodo.es_directorio:
                    ruta_actual.mkdir(exist_ok=True)
                    for hijo in nodo.hijos:
                        crear_recursivo(hijo, ruta_actual)
                else:
                    ruta_actual.touch(exist_ok=True)
            except Exception as e:
                logger.error(f"Error del sistema de archivos al procesar {ruta_actual}: {e}", exc_info=True)
                raise 

        try:
            crear_recursivo(raiz, base_path)
            logger.info(f"Creación de estructura física completada.")
            return raiz
        except Exception as e:
            logger.error(f"Error fatal durante la creación física desde texto: {str(e)}", exc_info=True)
            return None

    def ruta_desde(self, ancestro: Nodo) -> list[Nodo]:
        ruta = []
        nodo_actual: Nodo | None = self
        while nodo_actual and nodo_actual != ancestro:
            ruta.append(nodo_actual)
            nodo_actual = nodo_actual.padre
        if nodo_actual == ancestro:
             ruta.append(ancestro)
        return ruta[::-1]
