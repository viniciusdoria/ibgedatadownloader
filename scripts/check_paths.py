import os


def check_path(path_to_check: str, is_file: bool = False):
    """
    Verifica se um caminho (diretório ou arquivo) existe e imprime o status.

    :param path_to_check: O caminho a ser verificado.
    :param is_file: Define se o caminho é um arquivo (True) ou diretório (False).
    """
    if is_file:
        exists = os.path.isfile(path_to_check)
        path_type = "Arquivo"
    else:
        exists = os.path.isdir(path_to_check)
        path_type = "Diretório"

    status = "OK" if exists else "NÃO ENCONTRADO"
    print(f"{path_type: <10} | {status: <15} | {path_to_check}")


def main():
    """
    Constrói e verifica todos os caminhos definidos no arquivo qgis.pth.
    """
    print("-" * 80)
    print("Verificando a existência dos caminhos definidos em qgis.pth...")
    print("-" * 80)

    # --- Simula a primeira linha do qgis.pth ---

    # 1. Define as variáveis base
    try:
        program_files = os.environ["ProgramFiles"]
    except KeyError:
        print(
            "ERRO: A variável de ambiente 'ProgramFiles' não foi encontrada. "
            "Este script precisa ser executado em um ambiente Windows."
        )
        return

    # Define os mesmos apelidos usados no .pth
    gdal = os.path.join("apps", "gdal")
    grass = os.path.join(
        "apps", "grass", "grass84"
    )  # Usando grass84 conforme solicitado
    qgis = os.path.join("apps", "qgis-ltr")
    qt = os.path.join("apps", "qt5")

    # Constrói o caminho raiz do QGIS (OSGEO4W_ROOT)
    osgeo4w_root = os.path.normcase(
        os.path.normpath(os.path.join(program_files, "QGIS 3.40.12"))
    )

    # 2. Constrói a lista de caminhos a partir das variáveis de ambiente
    # Apenas os que representam caminhos são incluídos
    env_paths_to_check = {
        "OSGEO4W_ROOT": (osgeo4w_root, False),
        "GDAL_DATA": (os.path.join(osgeo4w_root, gdal, "share", "gdal"), False),
        "GDAL_DRIVER_PATH": (
            os.path.join(osgeo4w_root, gdal, "lib", "gdalplugins"),
            False,
        ),
        "GEOTIFF_CSV": (os.path.join(osgeo4w_root, "share", "epsg_csv"), False),
        "GISBASE": (os.path.join(osgeo4w_root, grass), False),
        "GRASS_PROJSHARE": (os.path.join(osgeo4w_root, "share", "proj"), False),
        "GRASS_PYTHON": (os.path.join(osgeo4w_root, "bin", "python3.exe"), True),
        "O4W_QT_PREFIX": (os.path.join(osgeo4w_root, qt), False),
        "O4W_QT_BINARIES": (os.path.join(osgeo4w_root, qt, "bin"), False),
        "O4W_QT_HEADERS": (os.path.join(osgeo4w_root, qt, "include"), False),
        "O4W_QT_LIBRARIES": (os.path.join(osgeo4w_root, qt, "lib"), False),
        "O4W_QT_PLUGINS": (os.path.join(osgeo4w_root, qt, "plugins"), False),
        "O4W_QT_TRANSLATIONS": (os.path.join(osgeo4w_root, qt, "translations"), False),
        "PDAL_DRIVER_PATH": (
            os.path.join(osgeo4w_root, "apps", "pdal", "plugins"),
            False,
        ),
        "PROJ_LIB": (os.path.join(osgeo4w_root, "share", "proj"), False),
        "QGIS_PREFIX_PATH": (os.path.join(osgeo4w_root, qgis), False),
        "QT_PLUGIN_PATH (1)": (os.path.join(osgeo4w_root, qgis, "qtplugins"), False),
        "QT_PLUGIN_PATH (2)": (os.path.join(osgeo4w_root, qt, "plugins"), False),
        "SSL_CERT_DIR": (os.path.join(osgeo4w_root, "apps", "openssl", "certs"), False),
        "SSL_CERT_FILE": (
            os.path.join(osgeo4w_root, "bin", "curl-ca-bundle.crt"),
            True,
        ),
    }

    # 3. Verifica cada caminho
    print("Verificando variáveis de ambiente:\n")
    print(f"{'Tipo': <10} | {'Status': <15} | Caminho")
    print(f"{'-' * 10} | {'-' * 15} | {'-' * 52}")

    for name, (path, is_file) in sorted(env_paths_to_check.items()):
        check_path(path, is_file)

    # --- Simula a segunda e terceira linhas (PATH e DLLs) ---
    print("\n\nVerificando caminhos adicionados ao PATH e diretórios de DLL:\n")
    print(f"{'Tipo': <10} | {'Status': <15} | Caminho")
    print(f"{'-' * 10} | {'-' * 15} | {'-' * 52}")

    # Simula as variáveis necessárias para construir o PATH
    qgis_prefix_path = env_paths_to_check["QGIS_PREFIX_PATH"][0]
    gisbase = env_paths_to_check["GISBASE"][0]
    o4w_qt_prefix = env_paths_to_check["O4W_QT_PREFIX"][0]

    path_dirs_to_check = [
        os.path.join(qgis_prefix_path, "bin"),
        os.path.join(gisbase, "lib"),
        os.path.join(gisbase, "bin"),
        os.path.join(o4w_qt_prefix, "bin"),
        os.path.join(osgeo4w_root, "bin"),
    ]

    for path in path_dirs_to_check:
        check_path(path)

    print("\n" + "-" * 80)
    print("Verificação concluída.")
    print("-" * 80)


if __name__ == "__main__":
    main()
