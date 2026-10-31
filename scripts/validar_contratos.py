"""Valida todos los contratos y la configuración de fuentes. Lo ejecutan pre-commit y CI.

Comprueba que cada contrato se puede cargar, que cada fuente apunta a un contrato que existe
y que la clave de negocio de la fuente coincide con la clave del contrato.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datafwk.config import Contrato, cargar_fuentes, cargar_yaml  # noqa: E402
from datafwk.errores import ConfiguracionInvalida  # noqa: E402


def validar(raiz: Path = RAIZ) -> list[str]:
    errores: list[str] = []
    contratos: dict[str, Contrato] = {}

    for ruta in sorted((raiz / "contracts").rglob("*.yml")):
        relativa = ruta.relative_to(raiz).as_posix()
        try:
            contrato = Contrato.desde_dict(cargar_yaml(str(ruta)))
        except ConfiguracionInvalida as exc:
            errores.append(f"{relativa}: {exc}")
            continue
        if contrato.capa != ruta.parent.name:
            errores.append(f"{relativa}: capa '{contrato.capa}' no coincide con la carpeta '{ruta.parent.name}'")
        if contrato.tabla != ruta.stem:
            errores.append(f"{relativa}: tabla '{contrato.tabla}' no coincide con el nombre del fichero")
        contratos[relativa] = contrato

    for ruta in sorted((raiz / "config" / "fuentes").glob("*.yml")):
        relativa = ruta.relative_to(raiz).as_posix()
        try:
            fuentes = cargar_fuentes(cargar_yaml(str(ruta)))
        except ConfiguracionInvalida as exc:
            errores.append(f"{relativa}: {exc}")
            continue
        for fuente in fuentes.values():
            contrato = contratos.get(fuente.contrato)
            if contrato is None:
                aviso = f"la fuente '{fuente.nombre}' apunta a un contrato inexistente: {fuente.contrato}"
                errores.append(f"{relativa}: {aviso}")
            elif tuple(fuente.clave_negocio) != contrato.clave:
                errores.append(f"{relativa}: la clave de '{fuente.nombre}' no coincide con la de su contrato")

    return errores


if __name__ == "__main__":
    encontrados = validar()
    for e in encontrados:
        print(f"ERROR {e}")
    print(f"{len(encontrados)} errores" if encontrados else "Contratos y fuentes válidos")
    sys.exit(1 if encontrados else 0)
