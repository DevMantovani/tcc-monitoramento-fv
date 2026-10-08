@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto environment_ready

where py >nul 2>&1
if not errorlevel 1 goto create_with_py
where python >nul 2>&1
if not errorlevel 1 goto create_with_python

echo Python 3.11 a 3.13 nao foi encontrado.
echo Instale o Python pelo site https://www.python.org/downloads/ e execute este arquivo novamente.
pause
exit /b 1

:create_with_py
echo Criando o ambiente local na primeira execucao...
py -3 -m venv .venv
goto environment_ready

:create_with_python
echo Criando o ambiente local na primeira execucao...
python -m venv .venv

:environment_ready
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -e .
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pv_monitor.launcher
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" goto failed
exit /b 0

:failed
echo.
echo Nao foi possivel iniciar o painel. Leia a mensagem acima para identificar o motivo.
pause
exit /b 1
