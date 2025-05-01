# 🌳 Convertidor de Estructuras de Directorios v2.0.0

Una aplicación de escritorio construida con Python y Tkinter que permite visualizar, generar, crear y limpiar estructuras de directorios de manera intuitiva.

<table>
  <tr>
    <td><img src="src/img/previewBlack.png" alt="Vista previa principal" width="500"></td>
    <td><img src="src/img/previewBlack_cleanDirec.png" alt="Diálogo Limpiar Directorio" width="300"></td>
  </tr>
  <tr>
    <td align="center"><i>Vista principal (Tema Oscuro)</i></td>
    <td align="center"><i>Nuevo Diálogo de Limpieza</i></td>
  </tr>
</table>

## 📋 Características Principales (v2.0.0)

* 📁 **Visualización:** Carga y muestra la estructura de un directorio existente.
* 🖌️ **Formatos:** Genera la estructura en formato árbol simple (estilo Markdown) o con iconos descriptivos.
* 🚫 **Filtros de Generación:** Permite especificar patrones (nombres, extensiones, carpetas) para ignorar al generar la estructura visual desde un directorio.
* 📝 **Editor Integrado:** Edita manualmente la estructura con herramientas de formato (símbolos de árbol, indentación) y atajos de teclado. Soporta deshacer/rehacer (Ctrl+Z/Y).
* 🏗️ **Creación de Directorios:** Crea la estructura física de carpetas y archivos definida en el editor.
* 🧹 **Herramienta de Limpieza:**
    * Abre un diálogo independiente para limpiar un directorio seleccionado.
    * Permite seleccionar el directorio a limpiar desde el diálogo.
    * Opciones para eliminar directorios `__pycache__`.
    * Opciones para eliminar archivos `.log`.
    * Permite especificar patrones personalizados para eliminar.
    * Permite especificar patrones para **ignorar** durante la limpieza (protege archivos/carpetas).
    * Muestra una confirmación detallada antes de la eliminación permanente.
* 🎨 **Personalización:** Tema claro/oscuro y configuración de fuentes para la UI y el editor.
* 💾 **Guardar/Cargar:** Guarda la estructura generada o editada en archivos `.md` o `.txt`.
* 📋 **Portapapeles:** Copia la estructura actual al portapapeles.

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
    # Windows
    .\ConvDirEnv\Scripts\activate
    # macOS/Linux
    source ConvDirEnv/bin/activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta la aplicación:
    ```bash
    python main.py
    ```

## 🛠️ Uso

1.  **Cargar y Visualizar:**
    * (Opcional) Escribe patrones a ignorar en "Ignorar al generar".
    * Clic en "📂 Cargar Directorio" y selecciona la carpeta.
    * Usa el checkbox "Usar iconos" para cambiar vista.

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

## 🤝 Contribuir

Fork -> Branch -> Commit -> Push -> Pull Request. Sigue PEP 8.

## 📄 Licencia

MIT License.

## ✨ Agradecimientos

* Python, Tkinter, ttkthemes Community.

## 📬 Contacto

HabunoGD1809 - [@Franklin_1809](https://x.com/Franklin_1809) 🐦 - franklinjoel1809@gmail.com 📧
