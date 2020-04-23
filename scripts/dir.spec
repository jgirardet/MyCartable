# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../src/main/python/main.py'],
             pathex=['src/main/python'],
             binaries=[],
             datas=[('../data', 'mimesis/data'),('../binary', 'binary'),],
             hiddenimports=["pony.orm.dbproviders","pony.orm.dbproviders.sqlite"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
print(a.pathex)
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
