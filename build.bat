@echo off
echo Building binary...

pyinstaller --onefile --name RestWorkflow --icon=icon.ico --hidden-import=textual --paths=.venv\Lib\site-packages TUI.py

echo Copying binary to root folder...
move /Y dist\RestWorkflow.exe .\

echo Cleaning up...
rmdir /S /Q build dist __pycache__
del RestWorkflow.spec

echo Build complete!