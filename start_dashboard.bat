@echo off
title Blood Pressure Dashboard - DIAGNOSTYKA

REM Przejscie do folderu, w ktorym znajduje sie ten skrypt
cd /d "%~dp0"

echo [DIAGNOSTYKA] Skrypt zostal uruchomiony w folderze:
echo %cd%
echo.

echo Aktywacja srodowiska wirtualnego...
call .\.venv\Scripts\activate.bat

echo.
echo Uruchamianie aplikacji Dashboard...
python app.py

echo.
echo Aplikacja zostala zatrzymana.
pause