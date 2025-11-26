# Tradução do Plugin IBGE Data Downloader

Este diretório contém arquivos de tradução para o plugin IBGE Data Downloader.

## Estrutura dos Arquivos

- **`*.ts`**: Arquivos de tradução (Translation Source)

  - Formato XML com strings de origem e traduções
  - Editáveis com ferramentas como Qt Linguist
  - Exemplos: `ibgeDataDownloader_pt.ts`, `af.ts`

- **`*.qm`**: Arquivos de tradução compilados (Qt Message File)

  - Formato binário otimizado para leitura pelo Qt/QGIS
  - Gerados automaticamente a partir dos arquivos `.ts`
  - Deve ser commitado no repositório

- **`compile_translations.py`**: Script wrapper principal

  - Ponto de entrada para compilação
  - Chama `compile_translations_final.py`

- **`compile_translations_final.py`**: Compilador com suporte a fallback

  - Procura `lrelease` em vários locais
  - Localiza `lrelease.exe` em `../../tools/lrelease.exe`
  - Se lrelease não encontrado, cria stubs vazios

- **`test_qm.py`**: Teste para validar carregamento de arquivos .qm

## Como Compilar Traduções

### Método 1: Script Python

```bash
python ibgedatadownloader/i18n/compile_translations.py
```

### Método 2: Direto com lrelease

```bash
tools/lrelease.exe ibgedatadownloader/i18n/ibgeDataDownloader_pt.ts -qm ibgedatadownloader/i18n/ibgeDataDownloader_pt.qm
```

## Adicionando Novas Traduções

### 1. Criar arquivo .ts

Use Qt Linguist para criar um novo arquivo `.ts`:

```bash
tools/lrelease.exe -ts ibgedatadownloader/i18n/ibgeDataDownloader_es.ts
```

Ou edite manualmente um existente copiando a estrutura de `ibgeDataDownloader_pt.ts`.

### 2. Editar traduções

No arquivo `.ts`, localize as mensagens e adicione traduções:

```xml
<context>
    <name>IbgeDataDownloader</name>
    <message>
        <source>Download data from IBGE</source>
        <translation>Descargar datos del IBGE</translation>
    </message>
</context>
```

### 3. Compilar

Execute o script de compilação:

```bash
python ibgedatadownloader/i18n/compile_translations.py
```

Isso gerará `ibgeDataDownloader_es.qm`.

### 4. Registrar linguagem

No arquivo `ibgeDataDownloader.py`, atualize o carregamento de traduções se necessário.

## Ferramentas Incluídas

O projeto inclui:

- **`tools/lrelease.exe`** (v5.15.18)
  - Ferramenta oficial do Qt para compilar .ts em .qm
  - Não requer instalação adicional
  - Funciona em Windows

## Compatibilidade

- ✓ QGIS 3.40.12+
- ✓ Python 3.10+
- ✓ Qt 5.15+
- ✓ Windows 10/11

## Referências

- [Qt Linguist Documentation](https://doc.qt.io/qt-5/linguist-manager.html)
- [QGIS Plugin i18n](https://docs.qgis.org/3.28/en/docs/pyqgis_developer_cookbook/plugins/plugins.html#translate-the-gui)
- [Qt .ts Format](https://doc.qt.io/qt-5/linguist-ts-file-format.html)
