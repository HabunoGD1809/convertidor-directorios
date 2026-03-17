from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk, messagebox
import logging

from .custom_widgets import TagEntry

logger = logging.getLogger('ConvertidorDirectorios')

class UIComponents:
    def __init__(self, parent, styles, callbacks):
        self.parent = parent
        self.styles = styles
        self.callbacks = callbacks
        self.message_label = None
        self.message_frame = None
        self.tooltip = None
        self.preview_placeholder = 'Pega aquí tu estructura o carga un directorio...'
        self.preview_text: tk.Text | None = None

    def create_title_section(self):
        titulo_frame = ttk.Frame(self.parent, style='TFrame')
        titulo_frame.pack(fill=tk.X, pady=(0, 15))

        header_frame = ttk.Frame(titulo_frame, style='TFrame')
        header_frame.pack(fill=tk.X)

        titulo = ttk.Label(header_frame, text="Convertidor de Estructuras de Directorios", style='Title.TLabel')
        titulo.pack(side=tk.LEFT, pady=(0, 5), anchor='w')

        right_buttons = ttk.Frame(header_frame, style='TFrame')
        right_buttons.pack(side=tk.RIGHT, padx=5)

        prefs_button = ttk.Button(right_buttons, text="Preferencias", style='Custom.TButton', command=self.callbacks['abrir_preferencias'])
        prefs_button.pack(side=tk.RIGHT)
        self._create_tooltip(prefs_button, "Abrir el diálogo de preferencias (Tema, Fuentes)")
        return titulo_frame

    def create_options_section(self, usar_iconos_var, ignore_patterns_var, guardar_patrones_var):
        opciones_frame = ttk.LabelFrame(self.parent, text="🛠️ Opciones de Visualización y Generación", padding="10", style='TLabelframe')
        opciones_frame.pack(fill=tk.X, pady=(0, 10))

        row1_frame = ttk.Frame(opciones_frame, style='TFrame')
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        checkbox = ttk.Checkbutton(row1_frame, text="Usar iconos en la estructura", variable=usar_iconos_var, command=lambda: self.callbacks['actualizar_preview'](from_checkbox=True), style='TCheckbutton')
        checkbox.pack(side=tk.LEFT, padx=(0, 20))
        self._create_tooltip(checkbox, "Alternar entre vista con iconos (📁📄) y vista de árbol (├──└──) al cargar un directorio.")

        row2_frame = ttk.Frame(opciones_frame, style='TFrame')
        row2_frame.pack(fill=tk.X, pady=(5, 0))

        ignore_label = ttk.Label(row2_frame, text="Ignorar al generar (separado por comas):", style='Custom.TLabel')
        ignore_label.pack(side=tk.LEFT, padx=(0, 10))

        ignore_entry = TagEntry(row2_frame, ignore_patterns_var, self.styles)
        ignore_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_tooltip(ignore_entry, "Patrones a ignorar. Escribe y presiona 'Enter' o ',' para añadir.\nEj: *.log, __pycache__, .git")
        
        guardar_check = ttk.Checkbutton(row2_frame, text="💾 Guardar como predeterminados", variable=guardar_patrones_var, style='TCheckbutton')
        guardar_check.pack(side=tk.RIGHT, padx=(10, 0))
        self._create_tooltip(guardar_check, "Si se marca, los patrones introducidos aquí se recordarán la próxima vez que abras la aplicación.")

        return opciones_frame

    def create_buttons_section(self):
        botones_frame = ttk.Frame(self.parent, style='TFrame')
        botones_frame.pack(fill=tk.X, pady=(0, 10))

        buttons_config = [
            {"text": "📂 Cargar Directorio", "command": self.callbacks['convertir_directorio'], "desc": "Selecciona una carpeta para visualizar su estructura."},
            {"text": "🔨 Crear desde Estructura", "command": self.callbacks['crear_desde_estructura'], "desc": "Crea la estructura definida en el editor."}
        ]

        for btn_config in buttons_config:
            btn = ttk.Button(botones_frame, text=btn_config["text"], style='Custom.TButton', command=btn_config["command"])
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self._create_tooltip(btn, btn_config["desc"])
        return botones_frame

    def create_preview_section(self):
        preview_container = ttk.LabelFrame(self.parent, text="📝 Editor / Vista Previa de Estructura", padding="10", style='TLabelframe')

        instructions_frame = ttk.Frame(preview_container, style='TFrame')
        instructions_frame.pack(fill=tk.X, pady=(0, 5))

        instructions = [
            "• Usa los botones o atajos (Alt+U/E/L, Tab/Shift+Tab) para formatear.",
            "• Usa [↘️ Pegar Dentro] (Alt+V) o Click-Derecho para pegar una estructura DENTRO del nivel actual.",
            "• Presiona [Ctrl + F] para abrir el buscador dentro de la estructura."
        ]
        instruction_font = (self.styles.settings.get('ui_font_family', 'Segoe UI'), 9)
        for inst in instructions: ttk.Label(instructions_frame, text=inst, style='Custom.TLabel', font=instruction_font).pack(anchor=tk.W)

        self.message_frame = ttk.Frame(preview_container, style='TFrame', height=25)
        self.message_frame.pack(fill=tk.X, pady=(0, 5))
        self.message_frame.pack_propagate(False)

        toolbar_frame = ttk.Frame(preview_container, style='TFrame')
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        toolbar_buttons = [
            ("└── ", "Último elemento (Alt+U)", "└── "),
            ("├── ", "Elemento (Alt+E)", "├── "),
            ("│   ", "Línea vertical (Alt+L)", "│   "),
            ("Indent", "Aumentar indentación (Tab)", "    "),
            ("Unindent", "Disminuir indentación (Shift+Tab)", None),
            ("↘️ Pegar Dentro", "Pega el portapapeles DENTRO de la carpeta actual", "PASTE_NESTED"),
            ("🧹 Sin #", "Eliminar todos los comentarios (Líneas con #)", "CLEAN_COMMENTS")
        ]
        
        for text, tooltip, symbol in toolbar_buttons:
            btn = ttk.Button(toolbar_frame, text=text, style='Custom.TButton')
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            if symbol == "CLEAN_COMMENTS": btn.configure(command=self.eliminar_comentarios)
            elif symbol == "PASTE_NESTED": btn.configure(command=self._paste_nested_structure)
            elif symbol is not None: btn.configure(command=lambda s=symbol: self._insert_or_indent(s))
            elif text == "Unindent": btn.configure(command=self._unindent_line)
            self._create_tooltip(btn, tooltip)

        # --- SECCIÓN DEL BUSCADOR (Ctrl+F) ---
        self.search_frame = ttk.Frame(preview_container, style='TFrame')
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_search_change)
        
        ttk.Label(self.search_frame, text="🔍 Buscar:", style='Custom.TLabel').pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry.bind('<Return>', self._find_next)
        self.search_entry.bind('<Escape>', self.hide_search)
        
        ttk.Button(self.search_frame, text="↓ Sig", style='Custom.TButton', command=self._find_next, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="↑ Ant", style='Custom.TButton', command=self._find_prev, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="✕", style='Custom.TButton', command=self.hide_search, width=3).pack(side=tk.RIGHT, padx=5)
        
        self.match_label = ttk.Label(self.search_frame, text="", style='Custom.TLabel')
        self.match_label.pack(side=tk.LEFT, padx=10)

        # CONTENEDOR DE TEXTO
        self.text_container = ttk.Frame(preview_container, style='Preview.TFrame')
        self.text_container.pack(fill=tk.BOTH, expand=True)

        self.preview_text = tk.Text(self.text_container, **self.styles.get_text_widget_config(), undo=True, maxundo=-1, autoseparators=True)

        # Configuración visual de tags
        error_bg = self.styles.current_theme.get('error_color', '#ff6b6b')
        self.preview_text.tag_configure("error_highlight", background=error_bg, foreground="white")
        self.preview_text.tag_configure('search_highlight', background='#00a5ff', foreground='white')
        self.preview_text.tag_configure('search_active', background='#ffcd38', foreground='black')

        self.preview_text.bind("<KeyPress>", lambda e: self.preview_text.tag_remove("error_highlight", "1.0", tk.END) if self.preview_text else None)
        self.preview_text.bind("<Button-1>", lambda e: self.preview_text.tag_remove("error_highlight", "1.0", tk.END) if self.preview_text else None)

        self.preview_text.bind('<Alt-u>', lambda e: self._insert_or_indent("└── "))
        self.preview_text.bind('<Alt-e>', lambda e: self._insert_or_indent("├── "))
        self.preview_text.bind('<Alt-l>', lambda e: self._insert_or_indent("│   "))
        self.preview_text.bind('<Tab>', lambda e: self._handle_tab_or_indent(indent=True))
        self.preview_text.bind('<Shift-Tab>', lambda e: self._handle_tab_or_indent(indent=False))
        self.preview_text.bind('<Alt-v>', lambda e: self._paste_nested_structure())
        
        # Binding global para Ctrl+F
        self.parent.winfo_toplevel().bind('<Control-f>', self.show_search)

        y_scrollbar = ttk.Scrollbar(self.text_container, orient="vertical", command=self.preview_text.yview)
        x_scrollbar = ttk.Scrollbar(self.text_container, orient="horizontal", command=self.preview_text.xview)
        self.preview_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.preview_text.insert('1.0', self.preview_placeholder)
        self.preview_text.configure(fg='grey50')

        self.preview_text.bind('<FocusIn>', self._on_focus_in)
        self.preview_text.bind('<FocusOut>', self._on_focus_out)
        self._create_context_menu(self.preview_text)

        return preview_container, self.preview_text

    # --- MÉTODOS DEL BUSCADOR ---
    def show_search(self, event=None):
        if not self.preview_text: return "break"
        
        if not self.search_frame.winfo_ismapped():
            self.search_frame.pack(side=tk.TOP, fill=tk.X, before=self.text_container)
        self.search_entry.focus_set()
        try:
            sel = self.preview_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if sel and '\n' not in sel:
                self.search_var.set(sel)
                self.search_entry.select_range(0, tk.END)
        except tk.TclError:
            pass
        return "break"

    def hide_search(self, event=None):
        if not self.preview_text: return "break" 
        
        if self.search_frame.winfo_ismapped():
            self.search_frame.pack_forget()
        self.preview_text.tag_remove('search_highlight', '1.0', tk.END)
        self.preview_text.tag_remove('search_active', '1.0', tk.END)
        self.preview_text.focus_set()
        return "break"

    def _on_search_change(self, *args):
        if not hasattr(self, 'preview_text') or not self.preview_text: return
        self.preview_text.tag_remove('search_highlight', '1.0', tk.END)
        self.preview_text.tag_remove('search_active', '1.0', tk.END)
        
        query = self.search_var.get()
        self._search_matches = []
        self._current_match_idx = -1
        
        if not query:
            self.match_label.config(text="")
            return
            
        start_pos = '1.0'
        while True:
            start_pos = self.preview_text.search(query, start_pos, nocase=True, stopindex=tk.END)
            if not start_pos: break
            end_pos = f"{start_pos}+{len(query)}c"
            self.preview_text.tag_add('search_highlight', start_pos, end_pos)
            self._search_matches.append((start_pos, end_pos))
            start_pos = end_pos
            
        if self._search_matches:
            self._find_next()
        else:
            self.match_label.config(text="0 resultados")

    def _find_next(self, event=None):
        if not hasattr(self, '_search_matches') or not self._search_matches: return "break"
        self._current_match_idx = (self._current_match_idx + 1) % len(self._search_matches)
        self._highlight_current_match()
        return "break"

    def _find_prev(self, event=None):
        if not hasattr(self, '_search_matches') or not self._search_matches: return "break"
        self._current_match_idx = (self._current_match_idx - 1) % len(self._search_matches)
        self._highlight_current_match()
        return "break"

    def _highlight_current_match(self):
        if not self.preview_text: return
        
        self.preview_text.tag_remove('search_active', '1.0', tk.END)
        if 0 <= self._current_match_idx < len(self._search_matches):
            start, end = self._search_matches[self._current_match_idx]
            self.preview_text.tag_add('search_active', start, end)
            self.preview_text.see(start)
            self.match_label.config(text=f"{self._current_match_idx + 1} de {len(self._search_matches)}")

    # --- LÓGICA DE PEGADO ANIDADO ---
    def _paste_nested_structure(self, event=None):
        if not self.preview_text: return "break"
        try:
            clipboard_content = self.parent.clipboard_get()
            if not clipboard_content: return "break"
            
            if self.preview_text.get('1.0', 'end-1c').strip() == self.preview_placeholder: 
                self.preview_text.delete('1.0', tk.END)
                self.preview_text.configure(fg=self.styles.current_theme.get('preview_fg', '#000000'))
                self.preview_text.insert(tk.INSERT, clipboard_content)
                return "break"
                
            cursor_idx = self.preview_text.index(tk.INSERT)
            line_num = int(cursor_idx.split('.')[0])
            line_text = self.preview_text.get(f"{line_num}.0", f"{line_num}.end")

            match = re.match(r'^([│\s]*(?:[├└]──\s*)?)', line_text)
            base_prefix = match.group(1) if match else ""
            
            child_prefix = base_prefix.replace("├── ", "│   ").replace("└── ", "    ")
            if not base_prefix or (not "├──" in base_prefix and not "└──" in base_prefix):
                child_prefix = base_prefix + "    "
            
            pasted_lines = clipboard_content.split('\n')
            new_lines = []
            for p_line in pasted_lines:
                if p_line.strip() or p_line.startswith('│'):
                    new_lines.append(child_prefix + p_line)
            
            self.preview_text.edit_separator()
            self.preview_text.insert(f"{line_num}.end", "\n" + "\n".join(new_lines))
            self.preview_text.edit_separator()
            
            self.show_message("↘️ Estructura anidada pegada con éxito", "success")
        except tk.TclError:
            self.show_message("⚠️ Portapapeles vacío", "warning")
        except Exception as e:
            self.show_message(f"⚠️ Error al pegar anidado: {e}", "error")
        return "break"

    def eliminar_comentarios(self):
        if not self.preview_text: return
        content = self.preview_text.get("1.0", "end-1c")
        if content == self.preview_placeholder or not content.strip(): return
        
        lineas = content.split('\n')
        lineas_limpias = []
        for l in lineas:
            l = l.replace('\xa0', ' ')
            if l.lstrip().startswith('#'): continue
            l = re.sub(r'\s+#.*$', '', l).rstrip()
            lineas_limpias.append(l)
        
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", "\n".join(lineas_limpias))
        self.show_message("✅ Comentarios eliminados del editor", "success")

    def resaltar_error_linea(self, numero_linea: int):
        if not self.preview_text or numero_linea < 1: return
        self.preview_text.tag_remove("error_highlight", "1.0", tk.END)
        start_index = f"{numero_linea}.0"
        end_index = f"{numero_linea}.end"
        self.preview_text.tag_add("error_highlight", start_index, end_index)
        self.preview_text.see(start_index)

    def _handle_tab_or_indent(self, indent=True):
        if not self.preview_text: return "break"
        try:
             sel_start = self.preview_text.index(tk.SEL_FIRST)
             sel_end = self.preview_text.index(tk.SEL_LAST)
             start_line = int(sel_start.split('.')[0])
             end_line = int(sel_end.split('.')[0])
             if sel_end.split('.')[1] == '0' and start_line != end_line : end_line -= 1
             self.preview_text.edit_separator()
             for line_num in range(start_line, end_line + 1):
                 if indent: self._indent_line(line_num)
                 else: self._unindent_line(line_num)
             self.preview_text.edit_separator()
             self.preview_text.tag_add(tk.SEL, f"{start_line}.0", f"{end_line + 1}.0")
        except tk.TclError:
             if indent: self._insert_or_indent("    ")
             else:
                  cursor_pos = self.preview_text.index(tk.INSERT)
                  line_num = int(cursor_pos.split('.')[0])
                  self._unindent_line(line_num)
        return "break"

    def _indent_line(self, line_num):
        if not self.preview_text: return
        try: self.preview_text.insert(f"{line_num}.0", "    ")
        except tk.TclError as e: logger.warning(f"TclError indenting: {e}")

    def _unindent_line(self, line_num=None):
        if not self.preview_text: return "break"
        cursor_pos = None
        try:
            self.preview_text.edit_separator()
            current_line_num = line_num
            if line_num is None:
                 cursor_pos = self.preview_text.index(tk.INSERT)
                 current_line_num = int(cursor_pos.split('.')[0])
            if current_line_num is None: return "break"
            line_start = f"{current_line_num}.0"
            line_end = f"{current_line_num}.end"
            current_line = self.preview_text.get(line_start, line_end)
            removed_count = 0
            temp_line = current_line
            for _ in range(4):
                if temp_line.startswith(' '):
                    temp_line = temp_line[1:]
                    removed_count += 1
                else: break
            if removed_count > 0:
                self.preview_text.delete(line_start, line_end)
                self.preview_text.insert(line_start, temp_line)
                if line_num is None and cursor_pos:
                     cursor_col = int(cursor_pos.split('.')[1])
                     self.preview_text.mark_set(tk.INSERT, f"{current_line_num}.{max(0, cursor_col - removed_count)}")
            self.preview_text.edit_separator()
        except tk.TclError: pass
        return "break"

    def _insert_or_indent(self, text):
        if not self.preview_text: return
        try:
            is_placeholder = self.preview_text.get('1.0', 'end-1c').strip() == self.preview_placeholder
            if is_placeholder:
                 self.preview_text.delete('1.0', tk.END)
                 self.preview_text.configure(fg=self.styles.current_theme.get('preview_fg', '#000000'))
            self.preview_text.edit_separator()
            try:
                start = self.preview_text.index(tk.SEL_FIRST)
                end = self.preview_text.index(tk.SEL_LAST)
                self.preview_text.delete(start, end)
                self.preview_text.insert(start, text)
                self.preview_text.tag_remove(tk.SEL, "1.0", tk.END)
            except tk.TclError:
                cursor_pos = self.preview_text.index(tk.INSERT)
                self.preview_text.insert(cursor_pos, text)
            self.preview_text.edit_separator()
            self.preview_text.focus_set()
            self.preview_text.see(tk.INSERT)
        except Exception: self.show_message("⚠️ Error al insertar", "error")

    def _on_focus_in(self, event=None):
        if not self.preview_text: return
        if self.preview_text.get('1.0', 'end-1c').strip() == self.preview_placeholder:
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.configure(fg=self.styles.current_theme.get('preview_fg', '#000000'))

    def _on_focus_out(self, event=None):
        if not self.preview_text: return
        if not self.preview_text.get('1.0', 'end-1c').strip():
            self.preview_text.insert('1.0', self.preview_placeholder)
            self.preview_text.configure(fg='grey50')

    def _create_context_menu(self, text_widget):
        menu = tk.Menu(self.parent, tearoff=0, bg=self.styles.current_theme.get('bg_color'), fg=self.styles.current_theme.get('fg_color'))
        menu.add_command(label="Deshacer", accelerator="Ctrl+Z", command=lambda: self._try_widget_event(text_widget, "<<Undo>>"))
        menu.add_command(label="Rehacer", accelerator="Ctrl+Y", command=lambda: self._try_widget_event(text_widget, "<<Redo>>"))
        menu.add_separator()
        menu.add_command(label="Cortar", accelerator="Ctrl+X", command=lambda: self._try_widget_event(text_widget, "<<Cut>>"))
        menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self._try_widget_event(text_widget, "<<Copy>>"))
        menu.add_command(label="Pegar", accelerator="Ctrl+V", command=lambda: self._paste_with_validation(text_widget))
        menu.add_command(label="Pegar Dentro de Carpeta (Anidado)", accelerator="Alt+V", command=lambda: self._paste_nested_structure())
        menu.add_separator()
        menu.add_command(label="Buscar", accelerator="Ctrl+F", command=lambda: self.show_search())
        menu.add_command(label="Seleccionar Todo", accelerator="Ctrl+A", command=lambda: text_widget.tag_add(tk.SEL, "1.0", tk.END))
        
        def show_menu(event):
            try:
                has_selection = bool(text_widget.tag_ranges(tk.SEL))
                menu.entryconfig("Cortar", state="normal" if has_selection else "disabled")
                menu.entryconfig("Copiar", state="normal" if has_selection else "disabled")
            except tk.TclError: pass
            menu.tk_popup(event.x_root, event.y_root)
            
        text_widget.bind("<Button-3>", show_menu)

    def _try_widget_event(self, widget, event_name):
        try: widget.event_generate(event_name)
        except tk.TclError: pass

    def _paste_with_validation(self, text_widget):
        try:
            clipboard_content = self.parent.clipboard_get()
            if clipboard_content:
                if text_widget.get('1.0', 'end-1c').strip() == self.preview_placeholder: 
                    text_widget.delete('1.0', tk.END)
                    text_widget.configure(fg=self.styles.current_theme.get('preview_fg'))
                text_widget.insert(tk.INSERT, clipboard_content)
        except Exception: self.show_message("⚠️ Error al pegar.", "error")

    def create_action_buttons(self):
        acciones_frame = ttk.Frame(self.parent, style='TFrame')
        buttons_config = [
            ("📋 Copiar Estructura", self.callbacks['copiar_estructura'], "Copiar la estructura al portapapeles."),
            ("💾 Guardar Estructura", self.callbacks['guardar_estructura'], "Guardar la estructura en archivo Markdown."),
            ("🧹 Limpiar Directorio", self.callbacks['abrir_dialogo_limpieza'], "Abrir diálogo para eliminar archivos/carpetas.")
        ]
        for texto, comando, tooltip in buttons_config:
            btn = ttk.Button(acciones_frame, text=texto, style='Custom.TButton', command=comando)
            btn.pack(side=tk.LEFT, padx=5)
            self._create_tooltip(btn, tooltip)
        return acciones_frame

    def create_footer(self):
        footer_frame = ttk.Frame(self.parent, style='TFrame', height=20)
        footer_frame.pack_propagate(False)
        try: from src import __version__; version_text = f"v{__version__}"
        except ImportError: version_text = "v2.2.0"
        
        ttk.Label(footer_frame, text=version_text, style='Custom.TLabel').pack(side=tk.LEFT, padx=(5,0))
        ttk.Label(footer_frame, text="Creado por HabunoGD1809", style='Custom.TLabel').pack(side=tk.RIGHT, padx=(0,5))
        return footer_frame

    def show_message(self, message, message_type='info', duration=4000):
        if not self.message_frame or not self.message_frame.winfo_exists(): return
        if hasattr(self, '_message_clear_timer') and self._message_clear_timer:
             try: self.parent.after_cancel(self._message_clear_timer)
             except ValueError: pass
             self._clear_message()
             
        style_name = self.styles.get_message_style(message_type)
        self.message_label = ttk.Label(self.message_frame, text=message, style=style_name)
        self.message_label.pack(fill=tk.X, padx=5, pady=2, expand=False)
        
        if duration and duration > 0: 
            self._message_clear_timer = self.parent.after(duration, self._clear_message)
        else: self._message_clear_timer = None

    def _clear_message(self):
        if self.message_label and self.message_label.winfo_exists(): self.message_label.destroy()
        self.message_label = None; self._message_clear_timer = None

    def _create_tooltip(self, widget, text): ToolTip(widget, text, self.styles)


class ToolTip:
    def __init__(self, widget, text, styles):
        self.widget = widget; self.text = text; self.styles = styles
        self.tooltip_window = None; self.show_id = None; self.hide_id = None
        self.widget.bind("<Enter>", self.schedule_show, add='+')
        self.widget.bind("<Leave>", self.schedule_hide, add='+')
        self.widget.bind("<ButtonPress>", self.hide_tooltip, add='+')
        
    def schedule_show(self, event=None):
        self.cancel_scheduled_hide()
        if not self.tooltip_window and not self.show_id:
            self.show_id = self.widget.after(500, self.show_tooltip)
            
    def schedule_hide(self, event=None):
        self.cancel_scheduled_show()
        if self.tooltip_window and not self.hide_id:
            self.hide_id = self.widget.after(100, self.hide_tooltip)
            
    def cancel_scheduled_show(self):
        if self.show_id: self.widget.after_cancel(self.show_id); self.show_id = None
        
    def cancel_scheduled_hide(self):
        if self.hide_id: self.widget.after_cancel(self.hide_id); self.hide_id = None
        
    def show_tooltip(self, event=None):
        self.cancel_scheduled_show()
        if self.tooltip_window: return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tk.Toplevel(self.widget); self.tooltip_window.wm_overrideredirect(True)
        try: self.tooltip_window.wm_attributes("-topmost", True)
        except tk.TclError: pass
        self.tooltip_window.wm_geometry(f"+{int(x)}+{int(y)}")
        
        theme_colors = self.styles.current_theme
        tooltip_font = (self.styles.settings.get('ui_font_family', 'Segoe UI'), 9)
        ttk.Label(self.tooltip_window, text=self.text, justify=tk.LEFT,
                  background=theme_colors.get('tooltip_bg', theme_colors.get('text_bg')),
                  foreground=theme_colors.get('tooltip_fg', theme_colors.get('text_fg')),
                  relief=tk.SOLID, borderwidth=1, padding=(5, 3), font=tooltip_font).pack()
                  
    def hide_tooltip(self, event=None):
        self.cancel_scheduled_show(); self.cancel_scheduled_hide()
        if self.tooltip_window:
            try: self.tooltip_window.destroy()
            except tk.TclError: pass
            self.tooltip_window = None
