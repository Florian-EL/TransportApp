@echo off
cd /d "C:\Users\Florian\Documents\TransportApp"
xcopy /E /Y /I /Q ".\build\exe.win-amd64-3.10\data\*" ".\data\"
call venv\Scripts\activate.bat
python build_exe.py build
call venv\Scripts\deactivate.bat