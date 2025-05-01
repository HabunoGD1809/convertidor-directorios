# 🌳 Convertidor de Estructuras de Directorios v2.0.0 🚀

Visualiza, crea y limpia estructuras de directorios sin esfuerzo. Esta aplicación convierte árboles de carpetas en texto fácil de entender (¡y viceversa!), te ayuda a generar proyectos desde cero y mantiene tus espacios de trabajo ordenados eliminando archivos basura.

---

## ✨ Características Destacadas (v2.0.0)

* 📁 **Visualización Inteligente:** Carga cualquier directorio y obtén una vista instantánea.
* 🎨 **Doble Formato:** Elige entre vista clásica de árbol (`├── └──`) o moderna con iconos (`📄 📁 🐍`).
* 🚫 **Filtros Flexibles (Generación):** Define patrones (`*.tmp`, `node_modules/`) para **excluir** al visualizar.
* ✍️ **Editor Integrado:** Modifica o crea estructuras con formato rápido (símbolos, indentación) y Deshacer/Rehacer.
* 🏗️ **Creación Rápida:** Diseña tu estructura en texto y créala en tu disco duro.
* 🧹 **Limpieza Profunda (Diálogo Independiente):**
    * Selecciona cualquier carpeta a limpiar.
    * Elimina `__pycache__`, `.log`, o patrones personalizados.
    * **¡Protege tus archivos!** Define patrones a **ignorar** durante la limpieza.
    * Revisa antes de la **confirmación final**.
* ⚙️ **Personalización Total:** Tema claro/oscuro y fuentes ajustables.
* C/G **Portabilidad:** Copia al portapapeles o guarda en archivos `.md` / `.txt`.

---

## 🖼️ Vistas Previas

<table>
  <tr>
    <td align="center">
      <b>Vista Principal (Tema Oscuro)</b><br>
      <img src="src/img/v2.0.0/previewBlack.png" alt="Vista principal Tema Oscuro" width="450">
    </td>
    <td align="center">
      <b>Vista Principal (Tema Claro)</b><br>
      <img src="src/img/v2.0.0/previeWhite.png" alt="Vista principal Tema Claro" width="450">
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>Diálogo de Limpieza</b><br>
      <img src="src/img/v2.0.0/previewBlack_cleanDirec.png" alt="Diálogo Limpiar Directorio" width="450">
    </td>
    <td align="center">
      <b>Ejemplo Estructura (Iconos)</b><br>
      <img src="src/img/v2.0.0/previewBlackStructure.png" alt="Estructura con Iconos" width="450">
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <b>Vista Previa v1.0.0 (Interfaz Anterior)</b><br>
      <img src="src/img/v1.0.0/old_preview.png" alt="Vista previa v1.0.0" width="450">
    </td>
  </tr>
</table>

---

## 🚀 Instalación

### Prerrequisitos

* Python 3.10 o superior (recomendado).
* pip (gestor de paquetes de Python).

### Pasos de instalación

1.  Clona el repositorio:
    ```bash
    git clone [https://github.com/HabunoGD1809/convertidor-directorios.git](https://github.com/HabunoGD1809/convertidor-directorios.git)
    cd convertidor-directorios
    ```
2.  (Recomendado) Crea y activa un entorno virtual:
    ```bash
    python -m venv ConvDirEnv
    # Windows: .\ConvDirEnv\Scripts\activate
    # macOS/Linux: source ConvDirEnv/bin/activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta la aplicación:
    ```bash
    python main.py
    ```

---

## 🛠️ Uso

1.  **Cargar y Visualizar:**
    * (Opcional) Escribe patrones a ignorar en "Ignorar al generar".
    * Clic en "📂 Cargar Directorio" y selecciona la carpeta.
    * Usa "Usar iconos" para cambiar vista.

2.  **Editar/Crear Estructura Manual:**
    * Pega o escribe en el editor.
    * Usa botones (`└──`, `├──`, `│`, `Indent`, `Unindent`) o atajos (`Alt+U/E/L`, `Tab`, `Shift+Tab`).

3.  **Crear Directorios:**
    * Clic en "🔨 Crear desde Estructura".
    * Selecciona directorio padre y confirma.

4.  **Limpiar Directorio:**
    * Clic en "🧹 Limpiar Directorio".
    * En el diálogo, clic en "Seleccionar..." y elige la carpeta.
    * Marca/escribe qué **eliminar** (`__pycache__`, `.log`, personalizados).
    * (Opcional) Escribe qué **ignorar**.
    * Clic en "Buscar y Confirmar Eliminación...".
    * Revisa la lista y confirma la eliminación permanente.

5.  **Copiar/Guardar:** Usa los botones correspondientes.
6.  **Preferencias:** Cambia tema y fuentes.

---

## 🚀 Futuras Mejoras (Roadmap)

¡Siempre hay espacio para mejorar! Aquí hay algunas ideas y funcionalidades que podrían llegar en futuras versiones:

* **Validación Avanzada al Crear:**
    * `- [ ]` Ignorar automáticamente líneas de comentario (ej. `# Este es un comentario`) en el texto de la estructura al usar "Crear desde Estructura".
    * `- [ ]` Permitir definir caracteres o prefijos personalizados a ignorar durante la creación.
    * `- [ ]` Mejorar la detección de errores de sintaxis en la estructura pegada, idealmente señalando la línea problemática.
    * `- [ ]` Advertir o prevenir la creación si la estructura de texto contiene iconos (ej. `📁`, `📄`), ya que no representan nombres válidos de archivos/carpetas.
* **Exportación Flexible:**
    * `- [ ]` Exportar la estructura generada a otros formatos como JSON, YAML o lista de texto simple indentada.
* **Importación Versátil:**
    * `- [ ]` Importar y visualizar estructuras desde formatos como JSON o listas indentadas.
* **Comparación de Directorios:**
    * `- [ ]` Opción para cargar dos directorios y resaltar visualmente las diferencias en sus estructuras.
* **Plantillas de Proyecto:**
    * `- [ ]` Guardar y cargar plantillas comunes de estructuras de directorios (ej. paquete Python, proyecto web básico).
* **Interfaz Mejorada:**
    * `- [ ]` Implementar una vista de árbol interactiva (expandir/colapsar nodos) como alternativa al editor de texto plano.
    * `- [ ]` Permitir arrastrar y soltar una carpeta sobre la ventana para cargarla directamente.
* **Búsqueda y Filtrado:**
    * `- [ ]` Añadir una función de búsqueda dentro de la estructura mostrada en el editor.
    * `- [ ]` Filtrar la vista por tipo de archivo o nombre.
* **Personalización Avanzada:**
    * `- [ ]` Permitir al usuario definir sus propios mapeos de iconos para extensiones de archivo.

¡Las sugerencias y contribuciones son bienvenidas para hacer crecer este proyecto!

---

## 🤝 Contribuir

Fork -> Branch -> Commit -> Push -> Pull Request. Sigue PEP 8.

## 📄 Licencia

MIT License.

## ✨ Agradecimientos

* Python, Tkinter, ttkthemes Community.

## 📫 Contacto

HabunoGD1809 - [@Franklin_1809](https://x.com/Franklin_1809) 🐦 - franklinjoel1809@gmail.com 📧
