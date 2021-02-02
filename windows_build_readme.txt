To fix issue with distutils:

https://stackoverflow.com/a/43971456/11273722

Add mingw in the PATH variable (C:\mingw-w64\x86_64-7.1.0-posix-seh-rt_v5-rev0\mingw64\bin for me)
Test by opening command line and command gcc works 

1) Create distutils.cfg in C:\Python36\Lib\distutils
Add lines in that file:

[build]
compiler = mingw32

[build_ext]
compiler = mingw32

2) Manually applying this patch:
https://bugs.python.org/file40608/patch.diff

3) Manually downloading the file vcruntime140.dll and putting it in C:\Python36\libs
https://www.microsoft.com/en-us/download/details.aspx?id=52685


