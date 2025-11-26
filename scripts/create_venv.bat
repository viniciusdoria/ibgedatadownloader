@echo off

chcp 65001>nul

set QGIS_PYTHON=%OSGEO4W_ROOT%\apps\Python312\python.exe

:: Ler diretório de destino do ambiente virtual da linha de comando
:: Se nenhum argumento foi forncecido, usar o nome padrão: .venv
if "%~1" == "" (
    set VENV_FOLDER=.venv
) else (
    set VENV_FOLDER=%~1
)


:: Verificar que o arquivo Lib\site-packages\qgis.pth existe
:: e é a única coisa dentro da pasta do ambiente virtual
if not exist %VENV_FOLDER%\Lib\site-packages\qgis.pth (
    echo Arquivo %VENV_FOLDER%\Lib\site-packages\qgis.pth não encontrado.
    exit /B 1
)

for /F %%i in ('dir /B /L "%VENV_FOLDER%"') do (
    if not "%%i" == "lib" (
        echo Pasta %VENV_FOLDER% contém outros arquivos além de Lib\site-packages\qgis.pth
        exit /B 1
    )
)

for /F %%i in ('dir /B /L "%VENV_FOLDER%\Lib"') do (
    if not "%%i" == "site-packages" (
        echo Pasta %VENV_FOLDER%\Lib contém outros arquivos além de site-packages\qgis.pth
        exit /B 1
    )
)

for /F %%i in ('dir /B /L "%VENV_FOLDER%\Lib\site-packages"') do (
    if not "%%i" == "qgis.pth" (
        echo Pasta %VENV_FOLDER%\Lib\site-packages contém outros arquivos além de qgis.pth
        exit /B 1
    )
)


:: Criar ambiente
"%QGIS_PYTHON%" -m venv "%VENV_FOLDER%" --system-site-packages
if %errorlevel% neq 0 exit /B %errorlevel%

echo Ambiente virtual criado no diretório %VENV_FOLDER%
echo Ativando o ambiente criado...

call "%VENV_FOLDER%\Scripts\activate.bat"
if %errorlevel% neq 0 exit /B %errorlevel%

echo Copiando arquivo de correção sitecustomize.py...

copy "%~dp0sitecustomize.py" "%VENV_FOLDER%\Lib\site-packages\sitecustomize.py"
if %errorlevel% neq 0 exit /B %errorlevel%

echo Ambiente virtual ativado. Instalando dependências de desenvolvimento...

python -m pip install --upgrade pip setuptools uv
if %errorlevel% neq 0 exit /B %errorlevel%

uv pip sync .\requirements\development.txt
if %errorlevel% neq 0 exit /B %errorlevel%

echo Dependências de desenvolvimento instaladas. Instalando pre-commit no repositório local...

pre-commit install
if %errorlevel% neq 0 exit /B %errorlevel%

echo Instalando/atualizando debugpy...

"%QGIS_PYTHON%" -m pip install --upgrade --user pip setuptools debugpy
if %errorlevel% neq 0 exit /B %errorlevel%

echo Configurando git blame...

git config blame.ignoreRevsFile .git-blame-ignore-revs
if %errorlevel% neq 0 exit /B %errorlevel%

echo Preparação do ambiente concluída.
