#!/usr/bin/env python
"""Script para testar se o arquivo .qm é válido e pode ser carregado pelo QGIS."""

from pathlib import Path

from qgis.PyQt.QtCore import QSettings, QTranslator


def test_qm_file():
    """Testa carregamento do arquivo .qm português"""
    plugin_dir = Path(__file__).parent.parent
    qm_file = plugin_dir / "i18n" / "ibgeDataDownloader_pt.qm"

    print(f"Testando arquivo: {qm_file}")
    print(f"Existe: {qm_file.exists()}")
    print(f"Tamanho: {qm_file.stat().st_size if qm_file.exists() else 'N/A'} bytes")
    print()

    if not qm_file.exists():
        print("❌ Arquivo não encontrado!")
        return False

    # Tentar carregar com QTranslator
    translator = QTranslator()
    result = translator.load(str(qm_file))

    print(f"Carregamento com QTranslator: {'✓ OK' if result else '✗ FALHOU'}")

    if result:
        # Testar tradução
        try:
            locale = QSettings().value("locale/userLocale")[0:2]
            print(f"Locale do sistema: {locale}")
        except (TypeError, AttributeError):
            locale = "pt"
            print(f"Locale padrão: {locale}")

        print()
        print("Alguns testes de tradução:")
        print(
            f"  'Download data from IBGE' -> '{translator.translate('IbgeDataDownloader', 'Download data from IBGE')}'",
        )
        print(f"  'Output directory' -> '{translator.translate('IbgeDataDownloader', 'Output directory')}'")
        return True
    print("Possíveis motivos:")
    print("  - Arquivo .qm corrompido")
    print("  - Formato .qm inválido")
    print("  - Problemas de codificação")
    return False


if __name__ == "__main__":
    import sys

    sys.exit(0 if test_qm_file() else 1)
