@echo off

chcp 65001>nul

set QGIS_PYTHON=%OSGEO4W_ROOT%\apps\Python39\python.exe

:: Ler diretório de destino do ambiente virtual da linha de comando
:: Se nenhum argumento foi forncecido, usar o nome padrão: .venv
if "%~1" == "" (
    set VENV_FOLDER=.venv
) else (
    set VENV_FOLDER=%~1
)

echo Ativando o ambiente...

call "%VENV_FOLDER%\Scripts\activate.bat"
if %errorlevel% neq 0 exit /B %errorlevel%

echo Ambiente virtual ativado. Atualizando dependências de desenvolvimento...

python -m pip install --upgrade pip setuptools uv
if %errorlevel% neq 0 exit /B %errorlevel%

uv pip sync .\requirements\development.txt
if %errorlevel% neq 0 exit /B %errorlevel%

echo Dependências de desenvolvimento atualizadas. Atualizando debugpy...

"%QGIS_PYTHON%" -m pip install --upgrade --user pip setuptools debugpy
if %errorlevel% neq 0 exit /B %errorlevel%

echo Atualizando dependências de documentação...

"%QGIS_PYTHON%" -m pip install --upgrade --user -r .\requirements\documentation.txt
if %errorlevel% neq 0 exit /B %errorlevel%

echo Atualização concluída.
