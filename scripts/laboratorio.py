"""Configura y publica el laboratorio propio de Fabric a partir de un dotenv local."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import uuid
from pathlib import Path

import yaml

from scripts._entorno_local import leer, obligatorio

RAIZ = Path(__file__).resolve().parents[1]
PASOS = {
    "base": "01_base",
    "calidad": "02_calidad",
    "fallar": "03_fallar",
    "recuperar": "02_calidad",
    "scd2": "05_scd2",
}


class _Dumper(yaml.SafeDumper):
    """Sangra las listas bajo su clave, como exige la regla indentation de yamllint."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def escribir_yaml(ruta, datos):
    """Escribe YAML que pasa yamllint: listas sangradas, UTF-8 y finales LF también en Windows."""
    texto = yaml.dump(datos, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=120)
    with ruta.open("w", encoding="utf-8", newline="\n") as fichero:
        fichero.write(texto)


def nombres(datos):
    proyecto = obligatorio(datos, "PROYECTO")
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,39}", proyecto):
        raise ValueError("PROYECTO: entre 3 y 40 letras minúsculas, números o guiones")
    return {
        tipo: datos.get(f"WORKSPACE_{tipo}_NOMBRE") or f"{proyecto}-{sufijo}-dev"
        for tipo, sufijo in [("DATOS", "datos"), ("ING", "ing"), ("ANA", "ana")]
    }


def configurar(datos, raiz=RAIZ):
    if obligatorio(datos, "ENTORNO") != "dev":
        raise ValueError("El laboratorio docente se configura únicamente en dev")
    workspaces = nombres(datos)
    entorno = {
        "nombre": "dev",
        "workspace_datos": workspaces["DATOS"],
        "lakehouses": {c: f"lh_{c}" for c in ("bronze", "silver", "gold")},
        "ruta_config": "_framework",
    }
    if datos.get("LAKEHOUSE_ESQUEMA"):
        entorno["esquema"] = datos["LAKEHOUSE_ESQUEMA"]
    escribir_yaml(raiz / "config/entornos/dev.yml", entorno)
    # Sustitución en DEV: conserva la celda literal exigida por AGENTS.md.
    ruta = raiz / "fabric/ingenieria/parameter.yml"
    parametros = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    for item in parametros["find_replace"]:
        if item.get("item_type") == "Notebook" and "datos" in item["find_value"]:
            item["replace_value"]["DEV"] = workspaces["DATOS"]
    escribir_yaml(ruta, parametros)
    return workspaces


def checkpoint(paso, raiz=RAIZ):
    if paso == "incremental":
        ruta = raiz / "config/fuentes/crm.yml"
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        datos["fuentes"]["clientes_crm"]["extraccion"]["modo"] = "incremental"
        escribir_yaml(ruta, datos)
        return
    origen = raiz / "templates/workshop" / PASOS[paso]
    # Primero contratos; después configuración que los referencia.
    for carpeta in ("contracts", "config"):
        for fichero in (origen / carpeta).rglob("*.yml"):
            destino = raiz / fichero.relative_to(origen)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fichero, destino)
    if paso == "recuperar":
        ruta = raiz / "contracts/silver/lineas_devolucion.yml"
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        datos["version"] = 4
        escribir_yaml(ruta, datos)
    if paso == "base":
        for dominio in ("crm", "devoluciones"):
            ruta = raiz / f"config/fuentes/{dominio}.yml"
            datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
            for nombre, fuente in datos["fuentes"].items():
                fuente.pop("origen_sql")
                fuente.update(
                    formato="csv",
                    ruta_landing=f"landing/{dominio}/{nombre}/{nombre}.csv",
                    opciones_lectura={
                        "header": "true",
                        "inferSchema": "false",
                        "nullValue": "\\N",
                        "multiLine": "true",
                        "escape": '"',
                        "mode": "FAILFAST",
                    },
                )
                if dominio == "crm":
                    fuente["extraccion"]["columna_marca"] = "fecha_cambio"
            escribir_yaml(ruta, datos)


def publicar_datos(datos):
    from azure.identity import AzureCliCredential
    from azure.storage.filedatalake import DataLakeServiceClient

    # OneLake no admite mezclar el GUID del workspace con el nombre del item: ambos por nombre, como publicar_config.
    workspace = nombres(datos)["DATOS"]
    raiz = Path(datos.get("DATA_ROOT") or "data")
    entradas = [
        (d, n, raiz / "laboratorio" / f"{n}.csv")
        for d, n in [("crm", "clientes_crm"), ("devoluciones", "lineas_devolucion")]
    ]
    if not all(r.is_file() for _, _, r in entradas):
        raise ValueError("Primero ejecuta modificar_csv preparar")
    credencial = AzureCliCredential(tenant_id=obligatorio(datos, "AZURE_TENANT_ID"))
    with DataLakeServiceClient("https://onelake.dfs.fabric.microsoft.com", credential=credencial) as servicio:
        sistema = servicio.get_file_system_client(workspace)
        for dominio, nombre, ruta in entradas:
            destino = f"lh_bronze.Lakehouse/Files/landing/{dominio}/{nombre}/{nombre}.csv"
            sistema.get_file_client(destino).upload_data(ruta.read_bytes(), overwrite=True)
            print(f"Publicado {nombre}.csv")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "accion", choices=["configurar", "checkpoint", "datos", "config", "lakehouses", "notebooks", "wheel"]
    )
    parser.add_argument("--env-file", type=Path, default=Path(".env.alumno"))
    parser.add_argument("--paso", choices=[*PASOS, "incremental"])
    parser.add_argument("--wheel", default="dist/datafwk-0.3.0-py3-none-any.whl")
    args = parser.parse_args()
    datos = leer(args.env_file)
    if args.accion == "configurar":
        print(configurar(datos))
    elif args.accion == "checkpoint":
        if not args.paso:
            parser.error("checkpoint necesita --paso")
        checkpoint(args.paso)
        print(f"Checkpoint {args.paso} aplicado localmente; revisa el diff y publica config.")
    elif args.accion == "datos":
        publicar_datos(datos)
    else:
        from azure.identity import AzureCliCredential

        credencial = AzureCliCredential(tenant_id=obligatorio(datos, "AZURE_TENANT_ID"))
        if args.accion == "wheel":
            for clave in ("WS_ING_ID", "ENV_FWK_ID"):
                os.environ[clave] = str(uuid.UUID(obligatorio(datos, clave)))
        if args.accion in ("notebooks", "lakehouses"):
            from azure.identity import AzureCliCredential
            from fabric_cicd import FabricWorkspace, publish_all_items

            es_datos = args.accion == "lakehouses"
            workspace = FabricWorkspace(
                workspace_id=obligatorio(datos, "WS_DATOS_ID" if es_datos else "WS_ING_ID"),
                environment="DEV",
                repository_directory=str(RAIZ / "fabric" / ("datos" if es_datos else "ingenieria")),
                item_type_in_scope=["Lakehouse"] if es_datos else ["Notebook"],
                token_credential=AzureCliCredential(tenant_id=obligatorio(datos, "AZURE_TENANT_ID")),
            )
            publish_all_items(workspace)
        elif args.accion == "config":
            from scripts import publicar_config

            entorno = yaml.safe_load((RAIZ / "config/entornos/dev.yml").read_text(encoding="utf-8"))
            if entorno["workspace_datos"] != nombres(datos)["DATOS"]:
                raise ValueError("El YAML pertenece a otro proyecto; ejecuta configurar con este fichero de entorno")
            sys.argv = ["publicar_config", "--entorno", "dev"]
            publicar_config.main(credencial)
        elif args.accion == "wheel":
            from scripts import publicar_libreria

            sys.argv = ["publicar_libreria", "--wheel", args.wheel]
            publicar_libreria.main(credencial)


if __name__ == "__main__":
    main()
