# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/python/main.py'],
             pathex=['src/python'],
             binaries=[],
             datas=[('../src/data', 'data'),('../src/data/mimesis', 'mimesis')],
             hiddenimports=["pony.orm.dbproviders","pony.orm.dbproviders.sqlite"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='MyCartable',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='MyCartable')
