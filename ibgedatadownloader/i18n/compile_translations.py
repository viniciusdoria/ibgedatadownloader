#!/usr/bin/env python
"""Compilador de Traduções Qt (.ts -> .qm)

Este projeto inclui a ferramenta Qt Linguist (lrelease.exe) em:
    tools/lrelease.exe

Para compilar as traduções, execute:
    python ibgedatadownloader/i18n/compile_translations.py

Os arquivos .qm compilados serão salvos em:
    ibgedatadownloader/i18n/*.qm

Recompile as traduções após editar os arquivos .ts:
    1. Edite: ibgedatadownloader/i18n/*.ts (arquivo XML com traduções)
    2. Execute: python ibgedatadownloader/i18n/compile_translations.py
    3. Os novos .qm serão gerados automaticamente

NOTA: Os arquivos .qm são commitados no repositório para garantir que
o plugin funcione mesmo sem ferramentas de compilação instaladas.
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Executar o compilador final
    i18n_dir = Path(__file__).parent
    compile_script = i18n_dir / "compile_translations_final.py"

    if not compile_script.exists():
        print("[ERRO] compile_translations_final.py não encontrado")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(compile_script)], check=False)
    sys.exit(result.returncode)
