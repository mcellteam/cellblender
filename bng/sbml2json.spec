# -*- mode: python -*-
a = Analysis(['sbml2json.py'],
             hiddenimports=['_libsbml'],
             hookspath=None,
             runtime_hooks=None,
	      excludes=['PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui','matplotlib','IPython','PIL','X11','gtk','pandas','scipy','libicudata'])

pyz = PYZ(a.pure)



exe = EXE(pyz,
          a.scripts + [('O','','OPTION')],
	  a.binaries,
	  a.zipfiles,
          a.datas,
          name='sbml2json',
          debug=False,
          strip=None,
          upx=True,
          console=True )


