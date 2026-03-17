from __future__ import annotations

from pathlib import Path
import re
import os
import shutil
from datetime import datetime
import logging

logger = logging.getLogger('ConvertidorDirectorios')

CLEAN_PATTERNS = {
    'pycache': {'dirs': ['__pycache__']},
    'logs': {'files': ['*.log']}
}

class FileHandler:

    @staticmethod
    def _should_exclude(item_path: Path, exclude_patterns: list[str]) -> bool:
        if not exclude_patterns: return False
        item_name = item_path.name
        if item_name in exclude_patterns: return True
        
        for pattern in exclude_patterns:
            pattern = pattern.strip()
            if not pattern: continue
            if pattern.endswith(('/', '\\')):
                dir_name_pattern = pattern.rstrip('/\\')
                if item_name == dir_name_pattern and item_path.is_dir(): return True
            if pattern == item_name: return True
            try:
                if Path(item_name).match(pattern): return True
            except (re.error, ValueError): logger.warning(f"Patrón ignorado inválido: {pattern}"); continue
            
        try: 
            current = item_path.parent
            target_root = Path(os.getcwd()) 
            while current != current.parent and current != target_root:
                 parent_name = current.name
                 if parent_name in exclude_patterns: return True
                 for pattern in exclude_patterns:
                      pattern = pattern.strip()
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
    def generar_estructura_iconos(dir_path: str, level: int = 0, exclude_patterns: list[str] | None = None) -> str:
        if exclude_patterns is None: exclude_patterns = []
        result = []
        try:
            base_path = Path(dir_path)
            if not base_path.is_dir(): raise FileNotFoundError(f"Dir no existe: {dir_path}")
            items_to_process = []
            try: iterator = base_path.iterdir()
            except PermissionError: return "🚫 Acceso denegado" if level == 0 else f"{'  '*level}🚫 {base_path.name}/"
            
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
                except PermissionError: result.append(f"{indent}🚫 {item.name} (Denegado)")
                except OSError as oe: result.append(f"{indent}❓ {item.name} (Error OS: {oe.strerror})")
            return "\n".join(line for line in result if line)
        except Exception as e: return f"❌ Error: {e}"

    @staticmethod
    def generar_estructura_arbol(dir_path: str, level: int = 0, prefix="", exclude_patterns: list[str] | None = None) -> str:
        if exclude_patterns is None: exclude_patterns = []
        result = []
        try:
            base_path = Path(dir_path)
            if not base_path.is_dir(): raise FileNotFoundError(f"Dir no existe: {dir_path}")
            items_to_process = []
            try: iterator = base_path.iterdir()
            except PermissionError: return f"{prefix}🚫 {base_path.name}/"
            
            for item in iterator:
                 try:
                     if not FileHandler._should_exclude(item, exclude_patterns) and item.exists(): items_to_process.append(item)
                 except OSError as e: pass
                 
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
                except PermissionError: result.append(f"{line_prefix}🚫 {item.name} (Denegado)")
                except OSError as oe: result.append(f"{line_prefix}❓ {item.name} (Error OS: {oe.strerror})")
            return "\n".join(line for line in result if line or line.strip())
        except Exception as e: return f"{prefix}❌ Error en '{os.path.basename(dir_path)}': {e}"

    @staticmethod
    def validar_estructura_para_creacion(estructura: str) -> tuple[bool, str, int]:
        estructura_corregida = estructura.replace('\u00a0', ' ')
        if not estructura_corregida.strip(): return False, "Estructura vacía.", -1
        lineas = [line for line in estructura_corregida.split('\n') if line.strip()]
        last_indent = -1

        for i, line in enumerate(lineas):
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'): continue
            
            # Usar la misma matemática visual que el Nodo
            match = re.match(r'^([│\s]*(?:[├└]──\s*)?)', line)
            if match:
                current_indent = (len(match.group(1).replace('\t', '    ')) + 2) // 4
            else:
                current_indent = 0
                
            es_linea_valida = (stripped.startswith(('├──', '└──', '│')) or re.match(r'^[📁📄]?\s*[^│├└]', stripped) is not None)
            if not es_linea_valida: return False, f"Línea {i+1}: Formato no reconocido o inválido ('{line.strip()}').", i+1
            
            if i > 0:
                diff = current_indent - last_indent
                # No se puede saltar más de un nivel de profundidad de golpe (ej: de carpeta padre a nieto directo)
                if diff > 1: return False, f"Línea {i+1}: Salto de indentación excesivo o hijo huérfano.", i+1
            last_indent = current_indent
            
        return True, "OK", -1

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
        icons = {
            '.txt': '📝', '.md': '📋', '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.odt': '📄',
            '.xls': '📊', '.xlsx': '📊', '.ods': '📊', '.csv': '📈', '.ppt': '投影', '.pptx': '投影',
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.json': '📦', '.xml': '⚙️', 
            '.java': '☕', '.cpp': '🔧', '.c': '🔧', '.h': '🔧', '.cs': '♯', '.php': '🐘', 
            '.rb': '💎', '.swift': '🐦', '.kt': '🧊', '.go': '🐹', '.rs': '🦀', '.ts': '📜', 
            '.jsx': '⚛️', '.tsx': '⚛️', '.vue': '🖖', '.sh': '💲', '.bat': '🦇', '.ps1': ' PowerShell', 
            '.sql': '💾', '.yaml': '⚙️', '.yml': '⚙️', '.jpg': '🖼️', '.png': '🖼️', '.svg': '🎨',
            '.zip': '📦', '.exe': '⚙️', '.env': '🔒', 'Dockerfile': '🐳', '.db': '🗄️'
        }
        return icons.get(ext, '📄')

    @staticmethod
    def convertir_estructura_texto(texto_actual: str, a_iconos: bool) -> str:
        lineas = texto_actual.split('\n')
        nuevas_lineas = []

        for linea_actual in lineas:
            match_arbol = re.match(r'^(?P<prefix>(?:[│\s]|\s{4})*)(?P<connector>[├└]──\s)?(?P<name>.*)', linea_actual)
            match_iconos = re.match(r'^(?P<indent>\s*)(?P<icon>[📁📄📝📋📕📘📊📈投影🐍📜🌐🎨📦⚙️☕🔧♯🐘💎🐦🧊🐹🦀⚛️🖖💲🦇 PowerShell💾🔒🐳🗄️🖋️🚫])?\s?(?P<name>.*)', linea_actual)

            if a_iconos:
                if match_arbol:
                    prefix = match_arbol.group('prefix') or ''
                    name_part = match_arbol.group('name') or ''
                    indent = prefix.replace('│   ', '  ').replace('    ', '  ')
                    nombre_limpio = name_part.strip()
                    es_directorio = nombre_limpio.endswith('/')
                    nombre_limpio = nombre_limpio.rstrip('/')

                    if es_directorio: nuevas_lineas.append(f"{indent}📁 {nombre_limpio}/")
                    else: nuevas_lineas.append(f"{indent}{FileHandler._get_file_icon(Path(nombre_limpio).suffix)} {nombre_limpio}")
                else: nuevas_lineas.append(linea_actual) 
            else:
                if match_iconos:
                    indent = match_iconos.group('indent') or ''
                    name = match_iconos.group('name') or ''
                    nuevas_lineas.append(f"{indent}{name}")
                else: nuevas_lineas.append(linea_actual)
        
        if not a_iconos:
            procesado = []
            niveles_indent = {}
            for i, linea in enumerate(nuevas_lineas):
                indent_len = len(linea) - len(linea.lstrip(' '))
                if indent_len not in niveles_indent: niveles_indent[indent_len] = []
                niveles_indent[indent_len].append(i)

            lineas_a_modificar = {}
            for indent_len, indices in niveles_indent.items():
                hermanos_por_padre = {}
                for idx in indices:
                    padre_idx = -1
                    for j in range(idx - 1, -1, -1):
                        if (len(nuevas_lineas[j]) - len(nuevas_lineas[j].lstrip(' '))) < indent_len:
                            padre_idx = j; break
                    if padre_idx not in hermanos_por_padre: hermanos_por_padre[padre_idx] = []
                    hermanos_por_padre[padre_idx].append(idx)
                
                for padre, hermanos in hermanos_por_padre.items():
                    if not hermanos: continue
                    ultimo_hermano_idx = max(hermanos)
                    for idx in hermanos:
                        prefijo = "└── " if idx == ultimo_hermano_idx else "├── "
                        lineas_a_modificar[idx] = ' ' * indent_len + prefijo + nuevas_lineas[idx].lstrip(' ')

            for i, linea_original in enumerate(nuevas_lineas):
                 procesado.append(lineas_a_modificar[i] if i in lineas_a_modificar else linea_original)
            
            final_result = []
            for i, linea_actual in enumerate(procesado):
                linea_final = list(linea_actual)
                for j in range(len(linea_final)):
                    if j < len(linea_final) - 1 and linea_final[j] == ' ' and linea_final[j+1] == ' ':
                        es_necesaria_barra = False
                        for k in range(i + 1, len(procesado)):
                            linea_futura = procesado[k]
                            if len(linea_futura) > j:
                                if linea_futura[j] in ('│', '├'): es_necesaria_barra = True; break
                                if len(linea_futura.lstrip(' ')) < len(linea_actual.lstrip(' ')): break 
                        if es_necesaria_barra: linea_final[j] = '│'
                final_result.append("".join(linea_final))
            return "\n".join(final_result)
        return "\n".join(nuevas_lineas)

    @staticmethod
    def encontrar_archivos_para_limpiar(
        target_dir: str, clean_pycache: bool, clean_logs: bool,
        custom_patterns: list[str], ignore_patterns: list[str] | None = None
        ) -> list[str]:
        target_path = Path(target_dir).resolve()
        if not target_path.is_dir(): return []
        if ignore_patterns is None: ignore_patterns = []
        potential_items = set()
        
        if clean_pycache:
            try: [potential_items.add(p) for p in target_path.rglob('__pycache__') if p.is_dir()]
            except PermissionError: pass
        if clean_logs:
            try: [potential_items.add(p) for p in target_path.rglob('*.log') if p.is_file()]
            except PermissionError: pass
        for pattern in custom_patterns:
            try: [potential_items.add(match) for match in target_path.rglob(pattern) if match.exists()]
            except Exception: pass

        items_to_delete = set()
        for item_path in potential_items:
            resolved_item_path = item_path.resolve()
            if not FileHandler._is_path_ignored(resolved_item_path, target_path, ignore_patterns):
                items_to_delete.add(str(resolved_item_path))
        return sorted(list(items_to_delete))

    @staticmethod
    def _is_path_ignored(item_path: Path, root_path: Path, ignore_patterns: list[str]) -> bool:
         if not ignore_patterns: return False
         item_path = item_path.resolve(); root_path = root_path.resolve()
         if FileHandler._matches_ignore(item_path, ignore_patterns): return True
         try:
             current = item_path.parent
             while current != root_path and current != current.parent:
                  if FileHandler._matches_ignore(current, ignore_patterns): return True
                  current = current.parent
         except Exception: pass
         return False

    @staticmethod
    def _matches_ignore(path_to_check: Path, ignore_patterns: list[str]) -> bool:
         name = path_to_check.name; is_dir = path_to_check.is_dir()
         for pattern in ignore_patterns:
             pattern = pattern.strip()
             if not pattern: continue
             if name == pattern: return True
             if pattern.endswith(('/', '\\')) and name == pattern.rstrip('/\\') and is_dir: return True 
             try:
                  if Path(name).match(pattern): return True
             except (re.error, ValueError): continue
         return False

    @staticmethod
    def limpiar_directorio(
        target_dir: str, clean_pycache: bool, clean_logs: bool,
        custom_patterns: list[str], confirmed: bool = False,
        ignore_patterns: list[str] | None = None 
        ) -> tuple[int, int]:
        if not confirmed: return 0, 0
        target_path = Path(target_dir).resolve()
        if not target_path.is_dir(): return 0, 1

        items_to_delete_paths = FileHandler.encontrar_archivos_para_limpiar(
            target_dir, clean_pycache, clean_logs, custom_patterns, ignore_patterns=ignore_patterns
        )
        deleted_count = 0; error_count = 0
        if not items_to_delete_paths: return 0, 0
        
        items_sorted = sorted([Path(p) for p in items_to_delete_paths], key=lambda p: (p.is_file(), -len(p.parts)))

        for item_path in items_sorted:
            if not item_path.exists(): continue
            try:
                if item_path.is_file(): os.remove(item_path); deleted_count += 1
                elif item_path.is_dir():
                    if item_path == target_path: continue
                    shutil.rmtree(item_path); deleted_count += 1
            except Exception: error_count += 1
        return deleted_count, error_count
