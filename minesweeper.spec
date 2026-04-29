# -*- mode: python ; coding: utf-8 -*-

# 体积优先配置：
# 1) optimize=2 移除 assert 和 docstring
# 2) strip=True 尝试剥离符号
# 3) upx=True 若系统安装了 UPX 会进一步压缩
# 4) excludes 排除本项目不需要的大体积生态

a = Analysis(
    ['minesweeper.py'],
    pathex=[],
    binaries=[],
    datas=[('images', 'images')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'setuptools',
        'distutils',
        'pydoc',
        'unittest',
        'email',
        'html',
        'http',
        'xml',
        'xmlrpc',
        'sqlite3',
        'pydoc_data',
        'lib2to3',
        'tkinter.test',
        'PIL.ImageQt',
        'PIL.ImageChops',
        'PIL.ImageStat',
        'PIL.ImageMath',
        'PIL.ImageSequence',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='minesweeper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
