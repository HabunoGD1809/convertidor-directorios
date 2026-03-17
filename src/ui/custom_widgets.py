import tkinter as tk
from tkinter import ttk

class TagEntry(ttk.Frame):
    """Un Entry que convierte texto en 'Chips', con diseño Responsive (Wrap/Salto de línea automático)."""
    
    def __init__(self, parent, string_var: tk.StringVar, styles, *args, **kwargs):
        super().__init__(parent, style='TFrame', *args, **kwargs)
        self.string_var = string_var
        self.styles = styles
        self.tags = []

        theme = self.styles.current_theme
        
        # Contenedor principal absoluto (elimina márgenes invisibles)
        self.container = tk.Frame(
            self, 
            bg=theme.get('text_bg', '#ffffff'),
            highlightbackground=theme.get('border_color', '#cccccc'),
            highlightcolor=theme.get('select_bg', '#00a5ff'),
            highlightthickness=1,
            bd=0
        )
        self.container.pack(fill=tk.BOTH, expand=True)

        # Vinculamos el evento de redimensionamiento de ventana para recalcular el diseño
        self.container.bind("<Configure>", lambda e: self.after(10, self._arrange_tags))

        # El Entry real que captura el texto
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self.container, 
            textvariable=self.entry_var, 
            relief=tk.FLAT,
            bg=theme.get('text_bg', '#ffffff'),
            fg=theme.get('text_fg', '#000000'),
            insertbackground=theme.get('fg_color', '#000000'),
            font=(self.styles.settings.get('ui_font_family', 'Segoe UI'), 9)
        )
        
        # Eventos para crear el chip al poner coma, dar enter, o borrar
        self.entry.bind('<comma>', self._on_delimiter)
        self.entry.bind('<Return>', self._on_delimiter)
        self.entry.bind('<BackSpace>', self._on_backspace)
        
        # Si hacen clic en cualquier lugar vacío del área blanca, enfocamos el editor
        self.container.bind('<Button-1>', lambda e: self.entry.focus_set())

        self._load_from_var()

    def _arrange_tags(self):
        """Motor matemático que organiza los chips para que bajen de línea si no caben."""
        if not self.container.winfo_exists(): return
        width = self.container.winfo_width()
        if width <= 1: return # Aún no renderizado
        
        # Iniciar exactamente pegado al borde (sin márgenes fantasma)
        x, y = 2, 2
        max_height = 0
        
        children = self.container.winfo_children()
        
        tags_labels = [c for c in children if isinstance(c, tk.Label)]
        all_elements = tags_labels + [self.entry]
        
        for child in all_elements:
            child.update_idletasks()
            cw = child.winfo_reqwidth()
            ch = max(child.winfo_reqheight(), 24) # Altura mínima 
            
            # Comportamiento elástico para el espacio donde se escribe
            if child == self.entry:
                cw = max(80, width - x - 4)
                
            # ¿Chocamos con el borde derecho? => Salto a la línea de abajo
            if x + cw > width and x > 2:
                x = 2
                y += max_height + 2
                max_height = 0
                # Si bajó el área de texto, que ocupe todo el ancho disponible
                if child == self.entry:
                    cw = max(80, width - 4) 
            
            # Posicionamiento absoluto seguro
            child.place(x=x, y=y, width=cw, height=ch)
            
            # Avanzamos la coordenada 'x' para el siguiente elemento
            x += cw + 4 
            max_height = max(max_height, ch)
            
        # Ajustamos dinámicamente la altura del contenedor para empujar la interfaz de abajo
        total_height = y + max_height + 2
        if self.container.cget('height') != total_height:
            self.container.configure(height=total_height)

    def _on_delimiter(self, event):
        text = self.entry_var.get().strip(', ')
        if text:
            self.add_tag(text)
        self.entry_var.set('')
        self.entry.after(1, lambda: self.entry_var.set(''))
        return 'break'

    def _on_backspace(self, event):
        if not self.entry_var.get() and self.tags:
            self.remove_tag(self.tags[-1])

    def add_tag(self, text):
        if text and text not in self.tags:
            self.tags.append(text)
            self._render_tags()
            self._update_var()

    def remove_tag(self, text):
        if text in self.tags:
            self.tags.remove(text)
            self._render_tags()
            self._update_var()

    def _render_tags(self):
        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()

        theme = self.styles.current_theme
        for tag in self.tags:
            lbl = tk.Label(
                self.container, 
                text=f" {tag}  ✕ ", 
                cursor="hand2",
                bg=theme.get('select_bg', '#264f78'),
                fg='#ffffff',
                font=(self.styles.settings.get('ui_font_family', 'Segoe UI'), 9),
                relief=tk.FLAT
            )
            lbl.bind("<Button-1>", lambda e, t=tag: self.remove_tag(t))
            
        self._arrange_tags() # Re-calcular estructura visual

    def _update_var(self):
        self.string_var.set(','.join(self.tags))

    def _load_from_var(self):
        val = self.string_var.get()
        if val:
            for t in val.split(','):
                t = t.strip()
                if t: self.tags.append(t)
        self._render_tags()
