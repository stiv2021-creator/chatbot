@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
echo Instalando y arrancando el bot. Progreso en ejecucion.log ...
call :main > ejecucion.log 2>&1
echo.
echo El bot se detuvo. Revisa ejecucion.log
pause
exit /b

:main
echo ===== Inicio %date% %time%
if not exist .env if exist token.txt (
  for /f "usebackq delims=" %%T in ("token.txt") do echo TELEGRAM_TOKEN=%%T> .env
  del token.txt
  echo .env creado
)
where py >nul 2>&1 && (set "PY=py -3") || (set "PY=python")
%PY% --version
if not exist venv\Scripts\python.exe (
  echo ===== Creando entorno virtual
  %PY% -m venv venv || (echo ERROR_VENV & exit /b 1)
)
echo ===== Instalando dependencias
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install torch --index-url https://download.pytorch.org/whl/cpu || (echo ERROR_TORCH & exit /b 1)
venv\Scripts\python -m pip install -r requirements.txt || (echo ERROR_REQS & exit /b 1)
echo ===== Arrancando bot
venv\Scripts\python -u bot.py
echo ===== Bot terminado (codigo %errorlevel%)
exit /b
