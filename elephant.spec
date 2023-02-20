# -*- mode: python ; coding: utf-8 -*-
#
# 这是一个使用 pyinstall 打包成二进制可执行程序的配置文件
# 

block_cipher = None


a = Analysis(['bin/elephantd.py'],
             pathex=['./','./lib'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='elephantd',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir='/var/cache',
          console=True )
