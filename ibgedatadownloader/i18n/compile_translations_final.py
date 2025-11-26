#!/usr/bin/env python
"""
Solução de fallback para traduções sem lrelease.

Como não conseguimos compilar um arquivo .qm válido sem a ferramenta oficial do Qt,
esta solução oferece duas alternativas:

1. Se lrelease estiver disponível no PATH do sistema, usa-o normalmente
2. Senão, desabilita traduções com um aviso

O QGIS consegue funcionar sem traduções - vai apenas mostrar strings em inglês.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def find_lrelease():
    """Procura lrelease em vários locais"""
    paths_to_check = [
        # 1. Primeiro, verificar se existe no diretório tools do projeto
        Path(__file__).parent.parent.parent / "tools" / "lrelease.exe",
        # 2. Depois, verificar PATH do sistema
        "lrelease.exe",
        "lrelease",
        # 3. Venv
        Path(__file__).parent.parent.parent / ".venv" / "Scripts" / "lrelease.exe",
        # 4. Instalações Qt
        Path("C:/Program Files/Qt/5.15.18/bin/lrelease.exe"),
        Path("C:/Program Files/Qt/5.15.13/bin/lrelease.exe"),
        Path("C:/Qt/5.15.18/bin/lrelease.exe"),
        Path("C:/Qt/5.15.13/bin/lrelease.exe"),
    ]

    for path in paths_to_check:
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_file():
            return path_obj

        exe = shutil.which(str(path))
        if exe:
            return Path(exe)

    return None


def compile_with_lrelease(lrelease_path):
    """Usa lrelease para compilar traduções"""
    i18n_dir = Path(__file__).parent
    ts_files = sorted(i18n_dir.glob("*.ts"))

    print(f"[INFO] Usando lrelease: {lrelease_path}")
    print()

    failed = False
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"  {ts_file.name:40} ...", end=" ")

        try:
            result = subprocess.run(
                [str(lrelease_path), str(ts_file), "-qm", str(qm_file)], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                size = qm_file.stat().st_size
                print(f"✓ ({size} bytes)")
            else:
                print(f"✗ {result.stderr[:50]}")
                failed = True
        except Exception as e:
            print(f"✗ {str(e)[:50]}")
            failed = True

    return not failed


def create_stub_qm_files():
    """Cria arquivos .qm stub vazios (permitindo que plugin funcione sem traduções)"""
    i18n_dir = Path(__file__).parent
    ts_files = sorted(i18n_dir.glob("*.ts"))

    print("[AVISO] lrelease não disponível")
    print("[INFO] Criando stubs de tradução (plugin funcionará em inglês)")
    print()

    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"  {ts_file.name:40} ...", end=" ")

        # Magic header Qt + versão
        stub_data = bytes.fromhex("3cb8b476") + bytes.fromhex("00000002")

        try:
            qm_file.write_bytes(stub_data)
            print(f"✓ (stub {len(stub_data)} bytes)")
        except Exception as e:
            print(f"✗ {e}")
            return False

    return True


if __name__ == "__main__":
    lrelease = find_lrelease()

    print("=" * 70)
    print("Compilador de Traduções Qt (.ts -> .qm)")
    print("=" * 70)
    print()

    if lrelease:
        success = compile_with_lrelease(lrelease)
    else:
        print("[AVISO] lrelease não encontrado no sistema")
        print()
        print("Alternativas:")
        print("  1. Instale manualmente Qt Linguist:")
        print("     https://www.qt.io/download-open-source")
        print()
        print("  2. Instale via pip (Windows apenas):")
        print("     pip install PyQt5-tools")
        print()
        print("Continuando com stubs de tradução...")
        print()

        success = create_stub_qm_files()

    print()
    if success:
        print("✓ Compilação concluída")
        sys.exit(0)
    else:
        print("✗ Erro durante compilação")
        sys.exit(1)
