from __future__ import annotations

from pathlib import Path
import re
import os
import shutil
from datetime import datetime
import logging

logger = logging.getLogger('ConvertidorDirectorios')

DEFAULT_EXCLUDE_PATTERNS = ['.git', '.svn', '.hg', '__pycache__', '.pytest_cache', '.venv', 'venv', 'env', 'node_modules', 'dist', 'build', '*.pyc', '*.pyo', '*.log', '.DS_Store']
CLEAN_PATTERNS = {
    'pycache': {'dirs': ['__pycache__']},
    'logs': {'files': ['*.log']}
}

class FileHandler:

    # --- _should_exclude, generar_*, validar_*, guardar_*, _get_file_icon remain unchanged ---
    @staticmethod
    def _should_exclude(item_path: Path, exclude_patterns: list[str]) -> bool:
        if not exclude_patterns: return False
        item_name = item_path.name
        if item_name in exclude_patterns: return True
        for pattern in exclude_patterns:
            pattern = pattern.strip();
            if not pattern: continue
            if pattern.endswith(('/', '\\')):
                dir_name_pattern = pattern.rstrip('/\\')
                if item_name == dir_name_pattern and item_path.is_dir(): return True
            if pattern == item_name: return True
            try:
                if Path(item_name).match(pattern): return True
            except (re.error, ValueError): logger.warning(f"Patrón ignorado inválido: {pattern}"); continue
        try: # Check parents
            current = item_path.parent; target_root = Path(os.getcwd()) # Improve root detection?
            while current != current.parent and current != target_root:
                 parent_name = current.name
                 if parent_name in exclude_patterns: return True
                 for pattern in exclude_patterns:
                      pattern = pattern.strip();
                      if not pattern: continue
                      if pattern.endswith(('/', '\\')):
                           if parent_name == pattern.rstrip('/\\'): return True
                      if parent_name == pattern: return True
                      try:
                           if Path(parent_name).match(pattern): return True
                      except (re.error, ValueError): pass
                 current = current.parent
        except Exception as e: logger.error(f"Error check parent ignore {item_path}: {e}")
        return False

    @staticmethod
    def generar_estructura_iconos(dir_path: str, level: int = 0, exclude_patterns=None) -> str:
        if exclude_patterns is None: exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
        result = []
        try:
            base_path = Path(dir_path)
            if not base_path.is_dir(): raise FileNotFoundError(f"Dir no existe: {dir_path}")
            items_to_process = []
            try: iterator = base_path.iterdir()
            except PermissionError: logger.error(f"Permiso denegado: {base_path}"); return "🚫 Acceso denegado" if level == 0 else f"{'  '*level}🚫 {base_path.name}/"
            for item in iterator:
                 try:
                     if not FileHandler._should_exclude(item, exclude_patterns) and item.exists(): items_to_process.append(item)
                 except OSError as e: logger.warning(f"Error OS check/exist gen iconos {item}: {e}")
            if not items_to_process:
                try: return "📂 Directorio vacío" if level == 0 and not any(base_path.iterdir()) else "📂 (Filtrado)" if level == 0 else ""
                except PermissionError: return "🚫 Acceso denegado" if level == 0 else ""
            items = sorted(items_to_process, key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items:
                indent = "  " * level
                try:
                    is_file = item.is_file(); is_dir = item.is_dir(); name = item.name
                    if is_file: result.append(f"{indent}{FileHandler._get_file_icon(item.suffix)} {name}")
                    elif is_dir:
                        result.append(f"{indent}📁 {name}/")
                        subdir_content = FileHandler.generar_estructura_iconos(str(item), level + 1, exclude_patterns)
                        if subdir_content and "🚫" not in subdir_content: result.append(subdir_content)
                        elif "🚫" in subdir_content: result.append(subdir_content)
                except PermissionError: logger.warning(f"Permiso denegado item gen iconos: {item}"); result.append(f"{indent}🚫 {item.name} (Denegado)")
                except OSError as oe: logger.warning(f"Error OS item gen iconos {item}: {oe}"); result.append(f"{indent}❓ {item.name} (Error OS: {oe.strerror})")
            return "\n".join(line for line in result if line)
        except FileNotFoundError: logger.error(f"Dir no encontrado gen iconos: {dir_path}"); return "❌ Dir no encontrado"
        except PermissionError: logger.error(f"Permiso denegado base gen iconos: {dir_path}"); return "🚫 Acceso denegado"
        except Exception as e: logger.error(f"Error inesperado gen iconos {dir_path}: {e}", exc_info=True); return f"❌ Error: {e}"

    @staticmethod
    def generar_estructura_arbol(dir_path: str, level: int = 0, prefix="", exclude_patterns=None) -> str:
        if exclude_patterns is None: exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
        result = []
        try:
            base_path = Path(dir_path)
            if not base_path.is_dir(): raise FileNotFoundError(f"Dir no existe: {dir_path}")
            items_to_process = []
            try: iterator = base_path.iterdir()
            except PermissionError: logger.error(f"Permiso denegado lista árbol: {base_path}"); return f"{prefix}🚫 {base_path.name}/"
            for item in iterator:
                 try:
                     if not FileHandler._should_exclude(item, exclude_patterns) and item.exists(): items_to_process.append(item)
                 except OSError as e: logger.warning(f"Error OS check/exist gen árbol {item}: {e}")
            if not items_to_process:
                try: return f"{prefix}└── Vacío" if level == 0 and prefix == "" and not any(base_path.iterdir()) else "" if level > 0 else f"{prefix}└── (Filtrado)"
                except PermissionError: return f"{prefix}🚫 Denegado" if level == 0 and prefix == "" else ""
            items = sorted(items_to_process, key=lambda x: (not x.is_dir(), x.name.lower()))
            for i, item in enumerate(items):
                is_last = i == len(items) - 1; sym = "└── " if is_last else "├── "; line_prefix = prefix + sym
                try:
                    is_file = item.is_file(); is_dir = item.is_dir(); name = item.name
                    if is_file: result.append(f"{line_prefix}{name}")
                    elif is_dir:
                        result.append(f"{line_prefix}{name}/")
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        subdir_content = FileHandler.generar_estructura_arbol(str(item), level + 1, next_prefix, exclude_patterns)
                        if subdir_content: result.append(subdir_content)
                except PermissionError: logger.warning(f"Permiso denegado item gen árbol: {item}"); result.append(f"{line_prefix}🚫 {item.name} (Denegado)")
                except OSError as oe: logger.warning(f"Error OS item gen árbol {item}: {oe}"); result.append(f"{line_prefix}❓ {item.name} (Error OS: {oe.strerror})")
            return "\n".join(line for line in result if line or line.strip())
        except FileNotFoundError: logger.error(f"Dir no encontrado gen árbol: {dir_path}"); return f"{prefix}❌ '{os.path.basename(dir_path)}' no encontrado"
        except PermissionError: logger.error(f"Permiso denegado base gen árbol: {dir_path}"); return f"{prefix}🚫 '{os.path.basename(dir_path)}'/"
        except Exception as e: logger.error(f"Error inesperado gen árbol {dir_path}: {e}", exc_info=True); return f"{prefix}❌ Error en '{os.path.basename(dir_path)}': {e}"

    @staticmethod
    def validar_estructura_para_creacion(estructura: str) -> tuple[bool, str]:
        """
        Valida si el formato del texto de la estructura es adecuado para la creación.
        Versión corregida para manejar espacios no separables y lógica de indentación.
        """
        # FIX: Reemplazar espacios no separables (nbsp) por espacios normales
        estructura_corregida = estructura.replace('\u00a0', ' ')

        if not estructura_corregida.strip():
            return False, "Estructura vacía."

        lineas = [line for line in estructura_corregida.split('\n') if line.strip()]
        last_indent = -1

        for i, line in enumerate(lineas):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            if not stripped:
                continue

            es_linea_valida = (
                stripped.startswith(('├──', '└──', '│')) or
                re.match(r'^[📁📄]?\s*[^│├└]', stripped) is not None
            )

            if not es_linea_valida:
                return False, f"Línea {i+1}: Formato no reconocido o inválido ('{line.strip()}')."

            # Comprobar saltos de indentación excesivos
            if i > 0:
                diff = current_indent - last_indent
                if diff > 0 and current_indent > last_indent + 6:
                    return False, f"Línea {i+1}: Indentación excesiva o inconsistente."

            last_indent = current_indent

        return True, "OK"

    @staticmethod
    def guardar_estructura(filename: str, estructura: str, usar_iconos: bool):
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encabezado = f"# Estructura Directorios\n# Generado: {fecha}\n# Modo: {'Iconos' if usar_iconos else 'Árbol'}\n# ---\n\n{estructura}\n"
            with open(filename, 'w', encoding='utf-8') as f: f.write(encabezado)
        except Exception as e: logger.error(f"Error guardando {filename}: {e}", exc_info=True); raise

    @staticmethod
    def _get_file_icon(ext: str) -> str:
        ext = ext.lower()
        icons = { '.txt':'📝','.md':'📋','.pdf':'📕','.doc':'📘','.docx':'📘','.odt':'📄','.xls':'📊','.xlsx':'📊','.ods':'📊','.csv':'📈','.ppt':'投影','.pptx':'投影','.odp':'投影','.py':'🐍','.js':'📜','.html':'🌐','.css':'🎨','.json':'📦','.xml':'⚙️','.java':'☕','.cpp':'🔧','.c':'🔧','.h':'🔧','.cs':'♯','.php':'🐘','.rb':'💎','.swift':'🐦','.kt':'🧊','.go':'🐹','.rs':'🦀','.ts':'📜','.jsx':'⚛️','.tsx':'⚛️','.vue':'🖖','.sh':'💲','.bash':'💲','.bat':'🦇','.ps1':' PowerShell','.sql':'💾','.yaml':'⚙️','.yml':'⚙️','.ini':'⚙️','.toml':'⚙️','.jpg':'🖼️','.jpeg':'🖼️','.png':'🖼️','.gif':'🖼️','.bmp':'🖼️','.svg':'🎨','.tif':'🖼️','.tiff':'🖼️','.webp':'🖼️','.ico':'🖼️','.mp3':'🎵','.wav':'🎵','.ogg':'🎵','.flac':'🎵','.aac':'🎵','.mp4':'🎥','.mkv':'🎥','.avi':'🎥','.mov':'🎥','.wmv':'🎥','.zip':'📦','.rar':'📦','.7z':'📦','.tar':'📦','.gz':'📦','.bz2':'📦','.exe':'⚙️','.dll':'⚙️','.so':'⚙️','.app':'📱','.dmg':'💿','.iso':'💿','.img':'💿','.log':'🗒️','.tmp':'⏳','.temp':'⏳','.bak':'💾','.gitignore':'🚫','.gitattributes':'⚙️','.env':'🔒','.lock':'🔒','.dockerfile':'🐳','Dockerfile':'🐳','.db':'🗄️','.sqlite':'🗄️','.sqlite3':'🗄️','.ttf':'🖋️','.otf':'🖋️','.woff':'🖋️','.woff2':'🖋️'}
        return icons.get(ext, '📄')

    # --- Cleaning methods remain unchanged, but _is_path_ignored is added ---
    @staticmethod
    def encontrar_archivos_para_limpiar(
        target_dir: str, clean_pycache: bool, clean_logs: bool,
        custom_patterns: list[str], ignore_patterns: list[str] | None = None
        ) -> list[str]:
        """Finds files/dirs matching clean patterns, excluding ignored ones."""
        target_path = Path(target_dir).resolve()
        if not target_path.is_dir(): logger.error(f"Dir limpieza no encontrado: {target_dir}"); return []
        if ignore_patterns is None: ignore_patterns = []
        final_ignore_patterns = ignore_patterns # Use only specified ignores for cleaning
        potential_items = set()
        # Find potential items (same as before)
        if clean_pycache:
            try: [potential_items.add(p) for p in target_path.rglob('__pycache__') if p.is_dir()]
            except PermissionError: logger.warning(f"Permiso denegado pycache {target_path}")
        if clean_logs:
            try: [potential_items.add(p) for p in target_path.rglob('*.log') if p.is_file()]
            except PermissionError: logger.warning(f"Permiso denegado logs {target_path}")
        for pattern in custom_patterns:
            try: [potential_items.add(match) for match in target_path.rglob(pattern) if match.exists()]
            except Exception as e: logger.warning(f"Patrón limpieza inválido '{pattern}'. {e}")

        # Filter using ignore patterns
        items_to_delete = set()
        for item_path in potential_items:
            resolved_item_path = item_path.resolve()
            if not FileHandler._is_path_ignored(resolved_item_path, target_path, final_ignore_patterns):
                items_to_delete.add(str(resolved_item_path))
            else: logger.debug(f"Ignorando para limpieza: {resolved_item_path} por: {final_ignore_patterns}")
        return sorted(list(items_to_delete))

    @staticmethod
    def _is_path_ignored(item_path: Path, root_path: Path, ignore_patterns: list[str]) -> bool:
         """Checks if item_path or its parents (up to root_path) match ignore patterns."""
         if not ignore_patterns: return False
         item_path = item_path.resolve(); root_path = root_path.resolve()
         # Check item itself
         if FileHandler._matches_ignore(item_path, ignore_patterns): return True
         # Check parents
         try:
             current = item_path.parent
             while current != root_path and current != current.parent:
                  if FileHandler._matches_ignore(current, ignore_patterns): return True
                  current = current.parent
             # Check root itself if needed? No, stop *at* root.
         except Exception as e: logger.error(f"Error check parent ignore {item_path}: {e}")
         return False

    @staticmethod
    def _matches_ignore(path_to_check: Path, ignore_patterns: list[str]) -> bool:
         """Checks if a specific path component name matches any ignore pattern."""
         name = path_to_check.name; is_dir = path_to_check.is_dir()
         for pattern in ignore_patterns:
             pattern = pattern.strip();
             if not pattern: continue
             if name == pattern: return True # Direct match
             if pattern.endswith(('/', '\\')) and name == pattern.rstrip('/\\') and is_dir: return True # Dir match
             try:
                  if Path(name).match(pattern): return True # Glob match
             except (re.error, ValueError): continue
         return False

    @staticmethod
    def limpiar_directorio(
        target_dir: str, clean_pycache: bool, clean_logs: bool,
        custom_patterns: list[str], confirmed: bool = False,
        ignore_patterns: list[str] | None = None # Add ignore here too for re-check
        ) -> tuple[int, int]:
        """Deletes files/dirs matching patterns, respecting ignores. Requires confirmation."""
        if not confirmed: logger.warning("Limpiar sin confirmación."); return 0, 0
        target_path = Path(target_dir).resolve();
        if not target_path.is_dir(): logger.error(f"Dir limpieza no encontrado: {target_dir}"); return 0, 1

        # Re-find files just before deleting for safety, applying ignores
        items_to_delete_paths = FileHandler.encontrar_archivos_para_limpiar(
            target_dir, clean_pycache, clean_logs, custom_patterns, ignore_patterns=ignore_patterns
        )
        deleted_count = 0; error_count = 0
        if not items_to_delete_paths: logger.info("No elementos a eliminar."); return 0, 0
        logger.info(f"Iniciando eliminación de {len(items_to_delete_paths)} elementos en {target_dir}...")
        items_sorted = sorted([Path(p) for p in items_to_delete_paths], key=lambda p: (p.is_file(), -len(p.parts)))

        for item_path in items_sorted:
            if not item_path.exists(): logger.info(f"Item ya no existe: {item_path}"); continue
            try:
                if item_path.is_file(): os.remove(item_path); logger.info(f"Archivo elim: {item_path}"); deleted_count += 1
                elif item_path.is_dir():
                    if item_path == target_path: logger.warning(f"Intento elim raíz: {item_path}. Omitiendo."); continue
                    shutil.rmtree(item_path); logger.info(f"Dir elim: {item_path}"); deleted_count += 1
                else: logger.warning(f"Item no es archivo/dir: {item_path}. Omitiendo.")
            except PermissionError as pe: logger.error(f"Permiso denegado elim {item_path}: {pe}"); error_count += 1
            except OSError as oe: logger.error(f"Error OS elim {item_path}: {oe}"); error_count += 1
            except Exception as e: logger.error(f"Error inesperado elim {item_path}: {e}", exc_info=True); error_count += 1
        logger.info(f"Eliminación: {deleted_count} elim, {error_count} errores")
        return deleted_count, error_count
