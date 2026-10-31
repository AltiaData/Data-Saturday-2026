"""Carga y validación de la configuración: entornos, fuentes y contratos.

En Fabric la configuración no vive en el workspace: el pipeline de despliegue la publica en
OneLake (Files/_framework/ del lakehouse de bronze) y los notebooks la leen desde ahí.
En local se lee del propio repositorio.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from datafwk.errores import ConfiguracionInvalida

Lector = Callable[[str], str]

CAPAS = ("bronze", "silver", "gold")
MODOS_CARGA = ("append", "overwrite", "merge")
POLITICAS_RECHAZO = ("cuarentena", "fallar")


def _lector_por_defecto(ruta: str) -> str:
    try:
        import notebookutils  # solo existe en Fabric

        return str(notebookutils.fs.head(ruta, 10_000_000))
    except ImportError:
        return Path(ruta).read_text(encoding="utf-8")


def cargar_yaml(ruta: str, lector: Lector | None = None) -> dict[str, Any]:
    contenido = (lector or _lector_por_defecto)(ruta)
    datos = yaml.safe_load(contenido) or {}
    if not isinstance(datos, dict):
        raise ConfiguracionInvalida(f"{ruta}: se esperaba un diccionario YAML")
    return datos


def _obligatorio(datos: dict[str, Any], clave: str, contexto: str) -> Any:
    if clave not in datos or datos[clave] in (None, ""):
        raise ConfiguracionInvalida(f"{contexto}: falta '{clave}'")
    return datos[clave]


# --------------------------------------------------------------------------- entorno


@dataclass(frozen=True)
class Entorno:
    nombre: str
    workspace_datos: str
    lakehouses: dict[str, str]
    esquema: str | None = None
    ruta_config: str = "_framework"

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Entorno:
        ctx = "entorno"
        lakehouses = _obligatorio(datos, "lakehouses", ctx)
        faltan = [c for c in CAPAS if c not in lakehouses]
        if faltan:
            raise ConfiguracionInvalida(f"{ctx}: faltan lakehouses para las capas {faltan}")
        return cls(
            nombre=_obligatorio(datos, "nombre", ctx),
            workspace_datos=_obligatorio(datos, "workspace_datos", ctx),
            lakehouses=dict(lakehouses),
            esquema=datos.get("esquema"),
            ruta_config=datos.get("ruta_config", "_framework"),
        )


# --------------------------------------------------------------------------- fuentes


@dataclass(frozen=True)
class Fuente:
    nombre: str
    dominio: str
    formato: str
    ruta_landing: str
    tabla_bronze: str
    tabla_silver: str
    clave_negocio: tuple[str, ...]
    contrato: str
    modo_carga: str = "merge"
    opciones_lectura: dict[str, str] = field(default_factory=dict)


def cargar_fuentes(datos: dict[str, Any]) -> dict[str, Fuente]:
    dominio = _obligatorio(datos, "dominio", "fuentes")
    resultado: dict[str, Fuente] = {}
    for nombre, cfg in (_obligatorio(datos, "fuentes", f"dominio {dominio}") or {}).items():
        ctx = f"fuente {dominio}.{nombre}"
        modo = cfg.get("modo_carga", "merge")
        if modo not in MODOS_CARGA:
            raise ConfiguracionInvalida(f"{ctx}: modo_carga '{modo}' no es uno de {MODOS_CARGA}")
        clave = tuple(_obligatorio(cfg, "clave_negocio", ctx))
        resultado[nombre] = Fuente(
            nombre=nombre,
            dominio=dominio,
            formato=_obligatorio(cfg, "formato", ctx),
            ruta_landing=_obligatorio(cfg, "ruta_landing", ctx),
            tabla_bronze=cfg.get("tabla_bronze", nombre),
            tabla_silver=cfg.get("tabla_silver", nombre),
            clave_negocio=clave,
            contrato=_obligatorio(cfg, "contrato", ctx),
            modo_carga=modo,
            opciones_lectura={k: str(v) for k, v in (cfg.get("opciones_lectura") or {}).items()},
        )
    return resultado


# --------------------------------------------------------------------------- contratos


@dataclass(frozen=True)
class Columna:
    nombre: str
    tipo: str
    nulo: bool = True
    valores: tuple[Any, ...] | None = None
    descripcion: str = ""


@dataclass(frozen=True)
class Regla:
    nombre: str
    expresion: str
    descripcion: str = ""


@dataclass(frozen=True)
class Contrato:
    tabla: str
    capa: str
    dominio: str
    propietario: str
    descripcion: str
    clave: tuple[str, ...]
    columnas: tuple[Columna, ...]
    reglas: tuple[Regla, ...] = ()
    politica_rechazo: str = "cuarentena"

    @property
    def nombres_columnas(self) -> tuple[str, ...]:
        return tuple(c.nombre for c in self.columnas)

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Contrato:
        tabla = _obligatorio(datos, "tabla", "contrato")
        ctx = f"contrato {tabla}"
        capa = _obligatorio(datos, "capa", ctx)
        if capa not in CAPAS:
            raise ConfiguracionInvalida(f"{ctx}: capa '{capa}' no es una de {CAPAS}")
        politica = datos.get("politica_rechazo", "cuarentena")
        if politica not in POLITICAS_RECHAZO:
            raise ConfiguracionInvalida(f"{ctx}: politica_rechazo '{politica}' no es una de {POLITICAS_RECHAZO}")

        columnas = []
        for nombre, cfg in (_obligatorio(datos, "columnas", ctx) or {}).items():
            valores = cfg.get("valores")
            columnas.append(
                Columna(
                    nombre=nombre,
                    tipo=_obligatorio(cfg, "tipo", f"{ctx}.{nombre}"),
                    nulo=bool(cfg.get("nulo", True)),
                    valores=tuple(valores) if valores else None,
                    descripcion=cfg.get("descripcion", ""),
                )
            )
        reglas = tuple(
            Regla(
                nombre=_obligatorio(r, "nombre", f"{ctx}.reglas"),
                expresion=_obligatorio(r, "expresion", f"{ctx}.reglas"),
                descripcion=r.get("descripcion", ""),
            )
            for r in datos.get("reglas") or []
        )
        clave = tuple(_obligatorio(datos, "clave", ctx))
        desconocidas = [c for c in clave if c not in {col.nombre for col in columnas}]
        if desconocidas:
            raise ConfiguracionInvalida(f"{ctx}: la clave usa columnas que no están en el contrato: {desconocidas}")

        return cls(
            tabla=tabla,
            capa=capa,
            dominio=_obligatorio(datos, "dominio", ctx),
            propietario=_obligatorio(datos, "propietario", ctx),
            descripcion=_obligatorio(datos, "descripcion", ctx),
            clave=clave,
            columnas=tuple(columnas),
            reglas=reglas,
            politica_rechazo=politica,
        )


def cargar_contrato(ruta: str, lector: Lector | None = None) -> Contrato:
    return Contrato.desde_dict(cargar_yaml(ruta, lector))
