@echo off

rem Root OSGEO4W home dir to the following directory
call "C:\OSGeo4W64\bin\o4w_env.bat"
call "C:\OSGeo4W64\bin\qt5_env.bat"
call "C:\OSGeo4W64\bin\py3_env.bat"

echo.
cmd /k python "pharmaceuticals_v0.1.py" 
@echo on