from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk, messagebox
import logging

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
        """Crea la sección del título"""
        titulo_frame = ttk.Frame(self.parent, style='TFrame')
        titulo_frame.pack(fill=tk.X, pady=(0, 15))

        header_frame = ttk.Frame(titulo_frame, style='TFrame')
        header_frame.pack(fill=tk.X)

        titulo = ttk.Label(
            header_frame,
            text="Convertidor de Estructuras de Directorios",
            style='Title.TLabel'
        )
        titulo.pack(side=tk.LEFT, pady=(0, 5), anchor='w')

        right_buttons = ttk.Frame(header_frame, style='TFrame')
        right_buttons.pack(side=tk.RIGHT, padx=5)

        prefs_button = ttk.Button(
            right_buttons,
            text="Preferencias",
            style='Custom.TButton',
            command=self.callbacks['abrir_preferencias']
        )
        prefs_button.pack(side=tk.RIGHT)
        self._create_tooltip(prefs_button, "Abrir el diálogo de preferencias (Tema, Fuentes)")
        # --- ADD RETURN ---
        return titulo_frame


    def create_options_section(self, usar_iconos_var, ignore_patterns_var):
        """Crea la sección de opciones principales y patrones a ignorar."""
        opciones_frame = ttk.LabelFrame(
            self.parent,
            text="🛠️ Opciones de Visualización y Generación",
            padding="10",
            style='TLabelframe'
        )
        opciones_frame.pack(fill=tk.X, pady=(0, 10))

        row1_frame = ttk.Frame(opciones_frame, style='TFrame')
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        checkbox = ttk.Checkbutton(
            row1_frame,
            text="Usar iconos en la estructura",
            variable=usar_iconos_var,
            command=lambda: self.callbacks['actualizar_preview'](from_checkbox=True),
            style='TCheckbutton'
        )
        checkbox.pack(side=tk.LEFT, padx=(0, 20))
        self._create_tooltip(checkbox, "Alternar entre vista con iconos (📁📄) y vista de árbol (├──└──) al cargar un directorio.")

        row2_frame = ttk.Frame(opciones_frame, style='TFrame')
        row2_frame.pack(fill=tk.X, pady=(5, 0))

        ignore_label = ttk.Label(
            row2_frame,
            text="Ignorar al generar (separado por comas):",
            style='Custom.TLabel'
        )
        ignore_label.pack(side=tk.LEFT, padx=(0, 10))

        ui_font_family = self.styles.settings.get('ui_font_family', 'Segoe UI')
        ui_font_size = self.styles.settings.get('ui_font_size', 10)
        entry_font = (ui_font_family, ui_font_size)

        ignore_entry = ttk.Entry(
            row2_frame,
            textvariable=ignore_patterns_var,
            width=50,
            font=entry_font
        )
        ignore_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._create_tooltip(ignore_entry, "Patrones a ignorar al 'Cargar Directorio'.\nEj: `*.log`, `__pycache__/`, `.git/`, `node_modules/`, `*.tmp`")

        default_info_label = ttk.Label(
             opciones_frame,
             text="Nota: `.git`, `.venv`, `__pycache__`, `node_modules` y otros comunes se ignoran por defecto.",
             style='Custom.TLabel',
             font=(ui_font_family, ui_font_size - 1)
        )
        default_info_label.pack(fill=tk.X, pady=(5,0), anchor='w')
        # --- ADD RETURN ---
        return opciones_frame


    def create_buttons_section(self):
        """Crea la sección de botones de carga/creación"""
        botones_frame = ttk.Frame(self.parent, style='TFrame')
        botones_frame.pack(fill=tk.X, pady=(0, 10))

        buttons_config = [
            {
                "text": "📂 Cargar Directorio",
                "command": self.callbacks['convertir_directorio'],
                "desc": "Selecciona una carpeta para visualizar su estructura en el editor (aplicando filtros de ignorados)."
            },
            {
                "text": "🔨 Crear desde Estructura",
                "command": self.callbacks['crear_desde_estructura'],
                "desc": "Crea la estructura de carpetas/archivos definida en el editor en la ubicación que elijas."
            }
        ]

        for btn_config in buttons_config:
            btn = ttk.Button(
                botones_frame,
                text=btn_config["text"],
                style='Custom.TButton',
                command=btn_config["command"]
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self._create_tooltip(btn, btn_config["desc"])
        # --- ADD RETURN ---
        return botones_frame


    def create_preview_section(self):
        """Crea la sección de vista previa/editor"""
        preview_container = ttk.LabelFrame(
            self.parent,
            text="📝 Editor / Vista Previa de Estructura",
            padding="10",
            style='TLabelframe'
        )
        # Pack is done in app.py now

        instructions_frame = ttk.Frame(preview_container, style='TFrame')
        instructions_frame.pack(fill=tk.X, pady=(0, 5))

        instructions = [
            "• Carga un directorio usando [📂 Cargar Directorio].",
            "• Pega una estructura existente o edita manualmente.",
            "• Usa los botones [└──], [├──], [│], [Indent], [Unindent] o atajos (Alt+U/E/L, Tab/Shift+Tab).",
            "• Usa [🔨 Crear desde Estructura] para generar carpetas/archivos.",
            "• Usa [🧹 Limpiar Directorio] (abajo) para eliminar archivos no deseados del directorio cargado."
        ]
        ui_font_family = self.styles.settings.get('ui_font_family', 'Segoe UI')
        ui_font_size = self.styles.settings.get('ui_font_size', 10)
        instruction_font = (ui_font_family, ui_font_size -1)
        for inst in instructions:
            ttk.Label(
                instructions_frame, text=inst, style='Custom.TLabel', font=instruction_font
            ).pack(anchor=tk.W)

        self.message_frame = ttk.Frame(preview_container, style='TFrame', height=25)
        self.message_frame.pack(fill=tk.X, pady=(0, 5))
        self.message_frame.pack_propagate(False)

        toolbar_frame = ttk.Frame(preview_container, style='TFrame')
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        toolbar_buttons = [
            ("└── ", "Insertar símbolo de último elemento (Alt+U)", "└── "),
            ("├── ", "Insertar símbolo de elemento (Alt+E)", "├── "),
            ("│   ", "Insertar línea vertical de continuación (Alt+L)", "│   "),
            ("Indent", "Aumentar indentación (Tab)", "    "),
            ("Unindent", "Disminuir indentación (Shift+Tab)", None)
        ]
        for text, tooltip, symbol in toolbar_buttons:
            btn = ttk.Button(toolbar_frame, text=text, style='Custom.TButton', width=8)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            if symbol is not None:
                btn.configure(command=lambda s=symbol: self._insert_or_indent(s))
            elif text == "Unindent":
                 btn.configure(command=self._unindent_line)
            self._create_tooltip(btn, tooltip)

        text_container = ttk.Frame(preview_container, style='Preview.TFrame')
        text_container.pack(fill=tk.BOTH, expand=True)

        self.preview_text = tk.Text(
            text_container, **self.styles.get_text_widget_config(),
            undo=True, maxundo=-1, autoseparators=True
        )

        self.preview_text.bind('<Alt-u>', lambda e: self._insert_or_indent("└── "))
        self.preview_text.bind('<Alt-U>', lambda e: self._insert_or_indent("└── "))
        self.preview_text.bind('<Alt-e>', lambda e: self._insert_or_indent("├── "))
        self.preview_text.bind('<Alt-E>', lambda e: self._insert_or_indent("├── "))
        self.preview_text.bind('<Alt-l>', lambda e: self._insert_or_indent("│   "))
        self.preview_text.bind('<Alt-L>', lambda e: self._insert_or_indent("│   "))
        self.preview_text.bind('<Tab>', lambda e: self._handle_tab_or_indent(indent=True))
        self.preview_text.bind('<Shift-Tab>', lambda e: self._handle_tab_or_indent(indent=False))

        y_scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.preview_text.yview)
        x_scrollbar = ttk.Scrollbar(text_container, orient="horizontal", command=self.preview_text.xview)
        self.preview_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.preview_text.insert('1.0', self.preview_placeholder)
        self.preview_text.configure(fg='grey50')

        self.preview_text.bind('<FocusIn>', self._on_focus_in)
        self.preview_text.bind('<FocusOut>', self._on_focus_out)

        self._create_context_menu(self.preview_text)

        # --- Return container AND text widget ---
        # app.py needs both references
        return preview_container, self.preview_text


    def _handle_tab_or_indent(self, indent=True):
        """Handles Tab and Shift+Tab for indenting/unindenting lines or inserting tab."""
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
        """Indents a specific line by inserting 4 spaces at the beginning."""
        if not self.preview_text: return
        try: self.preview_text.insert(f"{line_num}.0", "    ")
        except tk.TclError as e: logger.warning(f"TclError indenting line {line_num}: {e}")
        except Exception as e: logger.error(f"Error indenting line {line_num}: {e}", exc_info=True)

    def _unindent_line(self, line_num=None):
        """Unindents the current line or a specific line by removing up to 4 spaces."""
        if not self.preview_text: return "break"
        try:
            self.preview_text.edit_separator()
            current_line_num = line_num
            if line_num is None:
                 cursor_pos = self.preview_text.index(tk.INSERT)
                 current_line_num = int(cursor_pos.split('.')[0])
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
                if line_num is None:
                     cursor_line = int(cursor_pos.split('.')[0])
                     if cursor_line == current_line_num:
                          cursor_col = int(cursor_pos.split('.')[1])
                          new_col = max(0, cursor_col - removed_count)
                          self.preview_text.mark_set(tk.INSERT, f"{current_line_num}.{new_col}")
            self.preview_text.edit_separator()
        except tk.TclError as e: logger.warning(f"TclError unindent line {line_num}: {e}")
        except Exception as e: logger.error(f"Error unindenting line {line_num}: {e}", exc_info=True)
        return "break"

    def _insert_or_indent(self, text):
        """Inserts text (like symbols or spaces) at the cursor position or selection."""
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
        except tk.TclError as e: logger.warning(f"TclError inserting text '{text}': {e}")
        except Exception as e:
            logger.error(f"Error inserting symbol/text '{text}': {e}", exc_info=True)
            self.show_message("⚠️ Error al insertar texto", "error")

    def _on_focus_in(self, event=None):
        """Handles the text editor gaining focus."""
        if not self.preview_text: return
        content = self.preview_text.get('1.0', 'end-1c').strip()
        if content == self.preview_placeholder:
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.configure(fg=self.styles.current_theme.get('preview_fg', '#000000'))

    def _on_focus_out(self, event=None):
        """Handles the text editor losing focus."""
        if not self.preview_text: return
        content = self.preview_text.get('1.0', 'end-1c').strip()
        if not content:
            self.preview_text.insert('1.0', self.preview_placeholder)
            self.preview_text.configure(fg='grey50')

    def _create_context_menu(self, text_widget):
        """Crea un menú contextual mejorado para el widget de texto"""
        menu = tk.Menu(self.parent, tearoff=0,
                       bg=self.styles.current_theme.get('bg_color', '#FFFFFF'),
                       fg=self.styles.current_theme.get('fg_color', '#000000'))
        menu.add_command(label="Deshacer", accelerator="Ctrl+Z", command=lambda: self._try_widget_event(text_widget, "<<Undo>>"))
        menu.add_command(label="Rehacer", accelerator="Ctrl+Y", command=lambda: self._try_widget_event(text_widget, "<<Redo>>"))
        menu.add_separator()
        menu.add_command(label="Cortar", accelerator="Ctrl+X", command=lambda: self._try_widget_event(text_widget, "<<Cut>>"))
        menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self._try_widget_event(text_widget, "<<Copy>>"))
        menu.add_command(label="Pegar", accelerator="Ctrl+V", command=lambda: self._paste_with_validation(text_widget))
        menu.add_separator()
        menu.add_command(label="Seleccionar Todo", accelerator="Ctrl+A", command=lambda: self._select_all(text_widget))
        menu.add_separator()
        symbols_menu = tk.Menu(menu, tearoff=0,
                               bg=self.styles.current_theme.get('bg_color', '#FFFFFF'),
                               fg=self.styles.current_theme.get('fg_color', '#000000'))
        symbols_menu.add_command(label="└── Último elemento", accelerator="Alt+U", command=lambda: self._insert_or_indent("└── "))
        symbols_menu.add_command(label="├── Elemento", accelerator="Alt+E", command=lambda: self._insert_or_indent("├── "))
        symbols_menu.add_command(label="│   Línea vertical", accelerator="Alt+L", command=lambda: self._insert_or_indent("│   "))
        symbols_menu.add_separator()
        symbols_menu.add_command(label="Indentación", accelerator="Tab", command=lambda: self._handle_tab_or_indent(indent=True))
        symbols_menu.add_command(label="Quitar Indentación", accelerator="Shift+Tab", command=lambda: self._handle_tab_or_indent(indent=False))
        menu.add_cascade(label="Formato de Estructura", menu=symbols_menu)
        def show_menu(event):
            try:
                has_selection = bool(text_widget.tag_ranges(tk.SEL))
                menu.entryconfig("Cortar", state="normal" if has_selection else "disabled")
                menu.entryconfig("Copiar", state="normal" if has_selection else "disabled")
            except tk.TclError: menu.entryconfig("Cortar", state="disabled"); menu.entryconfig("Copiar", state="disabled")
            try: self.parent.clipboard_get(); menu.entryconfig("Pegar", state="normal")
            except tk.TclError: menu.entryconfig("Pegar", state="disabled")
            try:
                can_undo = text_widget.edit_undo()
                if can_undo: text_widget.edit_redo(); menu.entryconfig("Deshacer", state="normal")
                else: menu.entryconfig("Deshacer", state="disabled")
                can_redo = text_widget.edit_redo()
                if can_redo: text_widget.edit_undo(); menu.entryconfig("Rehacer", state="normal")
                else: menu.entryconfig("Rehacer", state="disabled")
            except tk.TclError: menu.entryconfig("Deshacer", state="disabled"); menu.entryconfig("Rehacer", state="disabled")
            menu.tk_popup(event.x_root, event.y_root)
        text_widget.bind("<Button-3>", show_menu)
        text_widget.bind("<Button-2>", show_menu)

    def _try_widget_event(self, widget, event_name):
        try: widget.event_generate(event_name)
        except tk.TclError as e: logger.warning(f"Error event '{event_name}': {e}")

    def _select_all(self, text_widget):
         try:
              text_widget.tag_add(tk.SEL, "1.0", tk.END)
              text_widget.mark_set(tk.INSERT, tk.END)
              text_widget.see(tk.INSERT)
         except tk.TclError as e: logger.warning(f"Error selecting all: {e}")

    def _paste_with_validation(self, text_widget):
        try:
            clipboard_content = self.parent.clipboard_get()
            if clipboard_content:
                is_placeholder = text_widget.get('1.0', 'end-1c').strip() == self.preview_placeholder
                if is_placeholder: text_widget.delete('1.0', tk.END); text_widget.configure(fg=self.styles.current_theme.get('preview_fg', '#000000'))
                text_widget.edit_separator()
                try:
                    start = text_widget.index(tk.SEL_FIRST); end = text_widget.index(tk.SEL_LAST)
                    text_widget.delete(start, end); text_widget.insert(start, clipboard_content)
                except tk.TclError:
                    cursor_pos = text_widget.index(tk.INSERT); text_widget.insert(cursor_pos, clipboard_content)
                text_widget.edit_separator(); text_widget.focus_set(); text_widget.see(tk.INSERT)
                from src.utils.file_handler import FileHandler
                current_content = text_widget.get('1.0', 'end-1c')
                is_valid, message = FileHandler.validar_estructura_para_creacion(current_content)
                if not is_valid: self.show_message(f"⚠️ Contenido pegado. {message}", "warning", duration = 5000)
            else: self.show_message("ℹ️ Portapapeles vacío.", "info", 2000)
        except tk.TclError: self.show_message("ℹ️ No texto en portapapeles.", "info", 2000)
        except ImportError: logger.error("Error importando FileHandler"); self._try_widget_event(text_widget, "<<Paste>>")
        except Exception as e:
             logger.error(f"Error pegado: {e}", exc_info=True); self._try_widget_event(text_widget, "<<Paste>>"); self.show_message("⚠️ Error al pegar.", "error")

    def _get_preview_content(self):
        if hasattr(self, 'preview_text') and self.preview_text and self.preview_text.winfo_exists():
            content = self.preview_text.get("1.0", "end-1c").strip()
            return "" if content == self.preview_placeholder else content
        return ""

    def create_action_buttons(self):
        """Crea los botones de acción inferiores (Copiar, Guardar, Limpiar)"""
        acciones_frame = ttk.Frame(self.parent, style='TFrame')
        # Pack is done in app.py now

        buttons_config = [
            ("📋 Copiar Estructura", self.callbacks['copiar_estructura'], "Copiar la estructura al portapapeles."),
            ("💾 Guardar Estructura", self.callbacks['guardar_estructura'], "Guardar la estructura en archivo Markdown."),
            ("🧹 Limpiar Directorio", self.callbacks['abrir_dialogo_limpieza'], "Abrir diálogo para eliminar archivos/carpetas del directorio cargado.")
        ]
        for texto, comando, tooltip in buttons_config:
            btn = ttk.Button(acciones_frame, text=texto, style='Custom.TButton', command=comando)
            btn.pack(side=tk.LEFT, padx=5)
            self._create_tooltip(btn, tooltip)
        # --- ADD RETURN ---
        return acciones_frame


    def create_footer(self):
        """Crea el pie de página"""
        footer_frame = ttk.Frame(self.parent, style='TFrame', height=20)
        # Pack is done in app.py now
        footer_frame.pack_propagate(False)

        try: from src import __version__; version_text = f"v{__version__}"
        except (ImportError, AttributeError): version_text = "v?.?.?"; logger.warning("Could not determine app version.")

        version_label = ttk.Label(footer_frame, text=version_text, style='Custom.TLabel')
        version_label.pack(side=tk.LEFT, padx=(5,0))
        firma = ttk.Label(footer_frame, text="Creado por HabunoGD1809", style='Custom.TLabel')
        firma.pack(side=tk.RIGHT, padx=(0,5))
        # --- ADD RETURN ---
        return footer_frame


    def show_message(self, message, message_type='info', duration=4000):
        if not self.message_frame or not self.message_frame.winfo_exists(): return
        if hasattr(self, '_message_clear_timer') and self._message_clear_timer:
             try: self.parent.after_cancel(self._message_clear_timer)
             except ValueError: pass
             self._clear_message()
        style_name = self.styles.get_message_style(message_type)
        self.message_label = ttk.Label(self.message_frame, text=message, style=style_name, wraplength=max(300, self.message_frame.winfo_width() - 20))
        self.message_label.pack(fill=tk.X, padx=5, pady=2, expand=False)
        if duration and duration > 0: self._message_clear_timer = self.parent.after(duration, self._clear_message)
        else: self._message_clear_timer = None

    def _clear_message(self):
        if self.message_label and self.message_label.winfo_exists(): self.message_label.destroy()
        self.message_label = None; self._message_clear_timer = None

    def _create_tooltip(self, widget, text): ToolTip(widget, text, self.styles)

# --- Tooltip Class (Helper) ---
class ToolTip:
    # ... (Tooltip class implementation remains the same as previous version) ...
    def __init__(self, widget, text, styles):
        self.widget = widget; self.text = text; self.styles = styles
        self.tooltip_window = None; self.show_id = None; self.hide_id = None
        self._bind_events()
    def _bind_events(self):
        self.widget.bind("<Enter>", self.schedule_show, add='+')
        self.widget.bind("<Leave>", self.schedule_hide, add='+')
        self.widget.bind("<ButtonPress>", self.hide_tooltip, add='+')
    def schedule_show(self, event=None):
        self.cancel_scheduled_hide()
        if self.tooltip_window or self.show_id: return
        self.show_id = self.widget.after(500, self.show_tooltip)
    def schedule_hide(self, event=None):
        self.cancel_scheduled_show()
        if not self.tooltip_window or self.hide_id: return
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
        tooltip_font = (self.styles.settings.get('ui_font_family', 'Segoe UI'), self.styles.settings.get('ui_font_size', 9))
        label = ttk.Label(self.tooltip_window, text=self.text, justify=tk.LEFT,
                          background=theme_colors.get('tooltip_bg', theme_colors.get('text_bg', '#FFFFE0')),
                          foreground=theme_colors.get('tooltip_fg', theme_colors.get('text_fg', '#000000')),
                          relief=tk.SOLID, borderwidth=1, padding=(5, 3), font=tooltip_font)
        label.pack()
    def hide_tooltip(self, event=None):
        self.cancel_scheduled_show(); self.cancel_scheduled_hide()
        if self.tooltip_window:
            try:
                if self.tooltip_window.winfo_exists(): self.tooltip_window.destroy()
            except tk.TclError: pass
        self.tooltip_window = None
