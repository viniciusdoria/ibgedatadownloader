# Sobrescrever sitecustomize.py do QGIS para evitar erro de '.'
# Este arquivo é carregado antes do sitecustomize.py do QGIS
import os

# Monkeypatch para os.add_dll_directory para evitar erro com '.'
if hasattr(os, 'add_dll_directory'):
    _original_add_dll_directory = os.add_dll_directory
    
    def patched_add_dll_directory(path):
        """Wrapper que filtra paths inválidos antes de adicionar"""
        # Ignorar caminho '.' (diretório atual)
        if path == '.' or path == '.\\' or path == './':
            return
        # Ignorar caminhos vazios
        if not path or not str(path).strip():
            return
        # Normalizar o caminho
        normalized_path = os.path.normcase(os.path.normpath(path))
        # Adicionar apenas se o diretório existir
        if os.path.isdir(normalized_path):
            try:
                _original_add_dll_directory(normalized_path)
            except (OSError, ValueError):
                # Ignorar erros silenciosamente
                pass
    
    # Substituir a função original
    os.add_dll_directory = patched_add_dll_directory
