@echo off

chcp 65001>nul

setlocal

set ORIGINALPATH=%PATH%

:: Script que configura as variáveis de ambiente e inicia o interpretador Python do QGIS.
set PYTHON_ENV_SCRIPT="%OSGEO4W_ROOT%\bin\python-qgis-ltr.bat"

:: Obter o caminho do sphinx-build.exe a partir da pasta site-packages do usuário.
for /f "usebackq tokens=*" %%i in (`%PYTHON_ENV_SCRIPT% -m site --user-site`) ^
do set SPHINXBUILD="%%i\..\Scripts\sphinx-build.exe"

:: Verificar se o executável do sphinx-build existe no caminho especificado.
%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.O comando 'sphinx-build' não foi encontrado. Certifique-se de que as dependências
	echo.de documentação estejam instaladas no Python do QGIS, não no ambiente virtual:
	echo.
	echo."%OSGEO4W_ROOT%\apps\Python39\python.exe" -m pip install -U --user -r .\requirements\documentation.txt
	echo.
	exit /b 1
)

:: Chamar o script apenas para configurar as variáveis de ambiente.
:: Passando -c pass porque o script inicia um interpretador Python.
call %PYTHON_ENV_SCRIPT% -c pass

:: Alterar o diretório de trabalho para o diretório acima do que contém este script
cd /D %~dp0..\

set SOURCEDIR=docs
set BUILDDIR=docs\_build

:: Se o builder não for especificado como parâmetro para este script, assumir html
if "%1" == "" (
    set BUILDER=html
) else (
    set BUILDER=%1
)

:: Se o builder tem "latex" no nome,
:: adiciona o PATH original ao PATH atual para encontrar o caminho da distribuição LaTeX
if NOT "%BUILDER%"=="%BUILDER:latex=%" path %PATH%;%ORIGINALPATH%

%SPHINXBUILD% -M %BUILDER% %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

endlocal
