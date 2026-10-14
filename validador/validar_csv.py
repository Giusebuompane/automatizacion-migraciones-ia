"""
Validador de CSV antes de cargarlos en el destino de una migración.

Comprobaciones deterministas sobre los CSV finales, sin necesitar la base de datos,
para detectar antes de cargar los fallos que más se han repetido entre migraciones.
No sustituye la revisión de una persona: es un primer filtro que se ejecuta siempre igual.

Uso:
    python validar_csv.py <carpeta_con_los_csv> [--sep ;]

Escribe el informe por consola y una copia en <carpeta>/audit_validacion_<fecha>.txt.
"""

import argparse
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

import pandas as pd

OK, WARN, FAIL = "OK", "WARN", "FAIL"
resultados = []


def registrar(fichero, comprobacion, estado, detalle=""):
    resultados.append((fichero, comprobacion, estado, detalle))


def leer(carpeta, nombre, sep):
    """Busca el CSV sin distinguir mayúsculas y lo lee todo como texto."""
    for ruta in carpeta.glob("*.csv"):
        if ruta.stem.lower() == nombre:
            return pd.read_csv(ruta, sep=sep, dtype=str, keep_default_na=False, encoding="utf-8")
    return None


def comprobar_bom(carpeta):
    for ruta in carpeta.glob("*.csv"):
        if ruta.read_bytes()[:3] == b"\xef\xbb\xbf":
            registrar(ruta.name, "Codificación UTF-8 sin BOM", FAIL, "el fichero empieza por BOM")
        else:
            registrar(ruta.name, "Codificación UTF-8 sin BOM", OK)


def comprobar_clientes(df):
    f = "clients.csv"
    # IDs duplicados
    if "ClientID" in df:
        dup = df["ClientID"][df["ClientID"].duplicated()].unique()
        registrar(f, "ClientID único", FAIL if len(dup) else OK, f"{len(dup)} IDs repetidos" if len(dup) else "")
        guid = df["ClientID"].str.fullmatch(r"[0-9a-fA-F-]{36}").sum()
        if guid:
            registrar(f, "ClientID numérico", FAIL, f"{guid} IDs con formato GUID: hay que traducirlos en la extracción")
    # Sexo desequilibrado: suele ser un valor por defecto que esconde datos desconocidos
    if "ClientSex" in df and len(df):
        reparto = df["ClientSex"].replace("", "(vacío)").value_counts(normalize=True)
        valor, peso = reparto.index[0], reparto.iloc[0]
        estado = WARN if peso > 0.85 and valor != "(vacío)" else OK
        registrar(f, "Reparto de sexo", estado, f"{peso:.0%} con '{valor}'")
    # DNI puramente numérico: probable teléfono o número interno capturado como documento
    if "ClientDNI" in df:
        sospechosos = df["ClientDNI"].str.fullmatch(r"\d{6,12}").sum()
        registrar(f, "DNI con letra de control", WARN if sospechosos else OK,
                  f"{sospechosos} DNI solo con números" if sospechosos else "")
    # Teléfonos compactados: nunca Phone1 vacío con Phone2 informado
    if {"ClientPhone1", "ClientPhone2"} <= set(df.columns):
        mal = ((df["ClientPhone1"] == "") & (df["ClientPhone2"] != "")).sum()
        registrar(f, "Teléfonos compactados", FAIL if mal else OK, f"{mal} clientes con Phone1 vacío y Phone2 informado" if mal else "")
    # Clientes ficticios usados para bloquear agenda
    if "ClientName" in df:
        patron = r"\b(?:OCUPADO|BLOQUEO|BLOQUEADO|TEST|PRUEBA|FESTIVO|VACACIONES|CERRADO)\b"
        ficticios = df["ClientName"].str.upper().str.contains(patron, regex=True).sum()
        registrar(f, "Clientes ficticios de bloqueo", WARN if ficticios else OK,
                  f"{ficticios} clientes con nombres de bloqueo: revisar sus citas" if ficticios else "")


def comprobar_huerfanos(df, nombre, columna, ids_clientes):
    if df is None or columna not in df or ids_clientes is None:
        return
    huerfanos = df.loc[~df[columna].isin(ids_clientes) & (df[columna] != ""), columna]
    registrar(f"{nombre}.csv", f"{columna} existe en clients", FAIL if len(huerfanos) else OK,
              f"{len(huerfanos)} filas de {huerfanos.nunique()} clientes inexistentes" if len(huerfanos) else "")


def comprobar_agenda(df):
    f = "diary_gen.csv"
    if "DiaryDate" not in df:
        return
    fechas = pd.to_datetime(df["DiaryDate"], errors="coerce", format="mixed")
    pasadas = (fechas.dt.date < date.today()).sum()
    invalidas = fechas.isna().sum()
    registrar(f, "Agenda solo con citas futuras", WARN if pasadas else OK, f"{pasadas} citas con fecha pasada" if pasadas else "")
    registrar(f, "Fechas de agenda válidas", FAIL if invalidas else OK, f"{invalidas} fechas no reconocidas" if invalidas else "")
    # Pista de dayfirst mal puesto: picos raros en un día de la semana concreto
    if fechas.notna().sum() > 50:
        domingos = (fechas.dt.dayofweek == 6).mean()
        if domingos > 0.10:
            registrar(f, "Patrón de días de la semana", WARN, f"{domingos:.0%} de citas en domingo: revisar si día y mes están intercambiados")


def comprobar_presupuestos(df):
    f = "budgets_gen.csv"
    if "BudgetDiscount" in df:
        desc = pd.to_numeric(df["BudgetDiscount"].str.replace(",", "."), errors="coerce")
        fuera = ((desc < 0) | (desc > 1)).sum()
        registrar(f, "Descuento entre 0 y 1", FAIL if fuera else OK, f"{fuera} líneas fuera de rango" if fuera else "")
    if {"BudgetGID", "BudgetID"} <= set(df.columns):
        # Cabecera y línea intercambiadas: el ID de cabecera no se repite y el de línea sí
        if df["BudgetGID"].is_unique and not df["BudgetID"].is_unique:
            registrar(f, "BudgetGID / BudgetID", FAIL, "parecen intercambiados: la cabecera debería repetirse en sus líneas")
        else:
            registrar(f, "BudgetGID / BudgetID", OK)


def comprobar_ficheros(df, nombre, columna):
    if df is None or columna not in df:
        return
    mayus = df[columna].str.contains(r"\.[A-Z0-9]{2,5}$", regex=True).sum()
    registrar(f"{nombre}.csv", "Extensión en minúsculas", FAIL if mayus else OK,
              f"{mayus} ficheros con la extensión en mayúsculas" if mayus else "")


def main():
    p = argparse.ArgumentParser(description="Valida los CSV de una migración antes de cargarlos")
    p.add_argument("carpeta", type=Path)
    p.add_argument("--sep", default=";")
    args = p.parse_args()
    carpeta = args.carpeta
    if not carpeta.is_dir():
        sys.exit(f"No existe la carpeta {carpeta}")

    comprobar_bom(carpeta)
    clientes = leer(carpeta, "clients", args.sep)
    ids = None
    if clientes is not None:
        comprobar_clientes(clientes)
        ids = set(clientes.get("ClientID", []))
    else:
        registrar("clients.csv", "Fichero presente", WARN, "no se ha encontrado; se omiten las comprobaciones de huérfanos")

    agenda = leer(carpeta, "diary_gen", args.sep)
    if agenda is not None:
        comprobar_agenda(agenda)
    presupuestos = leer(carpeta, "budgets_gen", args.sep)
    if presupuestos is not None:
        comprobar_presupuestos(presupuestos)
    for nombre, columna in (("clients_crm", "ClientID"), ("diary_gen", "DiaryClientID"),
                            ("budgets_gen", "BudgetClientID"), ("files", "FileClientID"), ("pictures", "PictureClientID")):
        df = {"diary_gen": agenda, "budgets_gen": presupuestos}.get(nombre)
        comprobar_huerfanos(df if df is not None else leer(carpeta, nombre, args.sep), nombre, columna, ids)
    comprobar_ficheros(leer(carpeta, "files", args.sep), "files", "FileName")
    comprobar_ficheros(leer(carpeta, "pictures", args.sep), "pictures", "PictureName")

    lineas = [f"Validación de {carpeta} - {datetime.now():%Y-%m-%d %H:%M}", ""]
    for estado in (FAIL, WARN, OK):
        for fichero, comprobacion, e, detalle in resultados:
            if e == estado:
                lineas.append(f"[{e:4}] {fichero:18} {comprobacion}" + (f": {detalle}" if detalle else ""))
    total = {e: sum(1 for r in resultados if r[2] == e) for e in (FAIL, WARN, OK)}
    lineas += ["", f"Resumen: {total[FAIL]} FAIL, {total[WARN]} WARN, {total[OK]} OK"]
    informe = "\n".join(lineas)
    # La consola de Windows (cp1252) no muestra bien los acentos: por pantalla solo ASCII, el fichero en UTF-8
    print(unicodedata.normalize("NFKD", informe).encode("ascii", "ignore").decode())
    (carpeta / f"audit_validacion_{datetime.now():%Y%m%d_%H%M%S}.txt").write_text(informe, encoding="utf-8")
    sys.exit(1 if total[FAIL] else 0)


if __name__ == "__main__":
    main()
