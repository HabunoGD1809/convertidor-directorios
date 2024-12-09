# -*- mode: python ; coding: utf-8 -*-

import os

# Definimos el directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.curdir)

# Construimos las rutas importantes
MAIN_SCRIPT = os.path.join(BASE_DIR, 'main.py')
SRC_DIR = os.path.join(BASE_DIR, 'src')
ICON_PATH = os.path.join(BASE_DIR, 'flecha-de-bucle.ico')

# Mensajes de diagnóstico para verificar las rutas
print(f"Directorio base: {BASE_DIR}")
print(f"Ruta del script principal: {MAIN_SCRIPT}")
print(f"Directorio src: {SRC_DIR}")
print(f"¿El script principal existe?: {os.path.exists(MAIN_SCRIPT)}")
print(f"¿El directorio src existe?: {os.path.exists(SRC_DIR)}")
print(f"Ruta del icono: {ICON_PATH}")
print(f"¿El icono existe?: {os.path.exists(ICON_PATH)}")

block_cipher = None

# Configuramos el Analysis para incluir solo los archivos necesarios
a = Analysis(
    [MAIN_SCRIPT],  # Usamos main.py como punto de entrada
    pathex=[
        BASE_DIR,
        SRC_DIR,  # Agregamos el directorio src al path
    ],
    binaries=[],
    datas=[
        # Incluimos solo el directorio src
        (SRC_DIR, 'src')
    ],
    hiddenimports=[
        'src.app'  # Aseguramos que el módulo app se incluya
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CODE - Structure Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mantenemos esto en True por ahora para ver posibles errores
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH
)
