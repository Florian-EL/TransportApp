@echo off
cd /d C:\Users\Florian\Documents\TransportApp
call venv\Scripts\activate.bat
python build_exe.py build
call venv\Scripts\deactivate.bat