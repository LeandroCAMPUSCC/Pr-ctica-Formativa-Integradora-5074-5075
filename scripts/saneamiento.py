from pathlib import Path
import argparse
import pandas as pd


# Rutas relativas a la estructura del proyecto.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_DIR / "datos" / "telemetria_envios.csv"
DEFAULT_OUTPUT = PROJECT_DIR / "datos" / "telemetria_limpia.csv"

# Estados admitidos según los valores catalogados en el dataset.
ESTADOS_VALIDOS = {
    "ENTREGADO",
    "EN_TRANSITO",
    "EN_REPARTO",
    "INCIDENCIA_REPARTO",
}

# Criterio de calidad adoptado para la telemetría de temperatura.
# El rango incluye todas las lecturas normales del fichero y excluye 98,4 ºC.
TEMP_MIN = -5.0
TEMP_MAX = 15.0

COLUMNAS_OBLIGATORIAS = {
    "id_envio",
    "id_vehiculo",
    "timestamp_lectura",
    "origen",
    "destino",
    "peso_kg",
    "temp_celsius",
    "latitud",
    "longitud",
    "estado_envio",
}

COLUMNAS_CRITICAS_NULAS = ["destino", "peso_kg", "temp_celsius"]


def sanear(input_path: Path, output_path: Path) -> None:
    """Lee, valida, depura y guarda el CSV saneado."""

    if not input_path.is_file():
        raise FileNotFoundError(
            f"No se encuentra el CSV de entrada: {input_path}\n"
            "Comprueba que telemetria_envios.csv está dentro de la carpeta datos."
        )

    # 1. Lectura del fichero original.
    df = pd.read_csv(input_path, encoding="utf-8")
    filas_iniciales = len(df)

    print("\n========== CONTROL DE CALIDAD ==========")
    print(f"Fichero de entrada: {input_path}")
    print(f"Registros originales: {filas_iniciales}")
    print(f"Columnas detectadas: {len(df.columns)}")

    # 2. Comprobar que el CSV contiene las columnas esperadas.
    faltantes = COLUMNAS_OBLIGATORIAS.difference(df.columns)
    if faltantes:
        raise ValueError(
            "El CSV no contiene todas las columnas esperadas. "
            f"Faltan: {', '.join(sorted(faltantes))}"
        )

    # 3. Asegurar que las columnas numéricas se pueden interpretar.
    # Los valores no convertibles pasan a NaN y se eliminan en el control de nulos.
    columnas_numericas = ["peso_kg", "temp_celsius", "latitud", "longitud"]
    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # 4. Eliminar filas completamente duplicadas.
    duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    print(f"Filas duplicadas eliminadas: {duplicados}")

    # 5. Eliminar registros con nulos en campos críticos.
    nulos = int(df[COLUMNAS_CRITICAS_NULAS].isna().any(axis=1).sum())
    df = df.dropna(subset=COLUMNAS_CRITICAS_NULAS).copy()
    print(f"Filas con nulos críticos eliminadas: {nulos}")

    # 6. Eliminar pesos no válidos (cero o negativos).
    peso_invalido = int((df["peso_kg"] <= 0).sum())
    df = df.loc[df["peso_kg"] > 0].copy()
    print(f"Filas con peso no positivo eliminadas: {peso_invalido}")

    # 7. Eliminar temperaturas fuera del rango definido.
    temperatura_invalida = int(
        (~df["temp_celsius"].between(TEMP_MIN, TEMP_MAX)).sum()
    )
    df = df.loc[df["temp_celsius"].between(TEMP_MIN, TEMP_MAX)].copy()
    print(
        "Filas con temperatura fuera del rango "
        f"[{TEMP_MIN}, {TEMP_MAX}] ºC eliminadas: {temperatura_invalida}"
    )

    # 8. Eliminar estados que no pertenecen al catálogo admitido.
    estado_invalido = int((~df["estado_envio"].isin(ESTADOS_VALIDOS)).sum())
    df = df.loc[df["estado_envio"].isin(ESTADOS_VALIDOS)].copy()
    print(f"Filas con estado no catalogado eliminadas: {estado_invalido}")

    # 9. Guardar el resultado sin índice de Pandas.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    filas_finales = len(df)
    eliminadas = filas_iniciales - filas_finales

    print("\n========== RESUMEN ==========")
    print(f"Registros originales: {filas_iniciales}")
    print(f"Registros finales:    {filas_finales}")
    print(f"Registros eliminados: {eliminadas}")
    print(f"Fichero generado:     {output_path}")
    print("\nDistribución de estados tras la limpieza:")
    print(df["estado_envio"].value_counts().to_string())
    print("\nSaneamiento finalizado correctamente.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Depura el CSV de telemetría logística con Pandas."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"CSV original (por defecto: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV saneado (por defecto: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    try:
        sanear(args.input, args.output)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        raise SystemExit(f"\nERROR: {error}") from error


if __name__ == "__main__":
    main()
