:: Configurar nome e caminho de destino do plugin
set PluginName=ibgedatadownloader
set PluginSourcePath=..\%PluginName%\%PluginName%
set PluginPath=%AppData%\QGIS\QGIS3\profiles\default\python\plugins\%PluginName%

:: Mudar o diretório de trabalho para o diretório deste script e salvar o diretório anterior numa pilha
pushd %~dp0

:: Compilar traduções (.ts -> .qm)
echo.
echo [COMPILANDO TRADUCOES]
cd ..\%PluginName%\i18n
python.exe compile_translations.py
if errorlevel 1 (
    echo [AVISO] Falha na compilacao de traducoes
    cd ..\..
)
cd ..\..\scripts

:: Espelhar o conteúdo atual da pasta de origem na pasta de destino
echo.
echo [FAZENDO DEPLOY DO PLUGIN]
robocopy "%PluginSourcePath%" "%PluginPath%" /MIR ^
    /XD "test" "__pycache__" "help" ^
    /XF "*.md" "*.pro" "*.ts" "*.pyc" "Makefile" "pb_tool.cfg" "pylintrc" ".gitignore" ".qgisignore"

:: Retornar ao diretório de trabalho inicial
popd

echo.
echo [CONCLUIDO] Plugin implantado em: %PluginPath%
