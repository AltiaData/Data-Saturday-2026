"""Sube el wheel de datafwk al Environment env_fwk y lo publica.

Usa la API REST de Fabric para Environments (staging + publish). Publicar un Environment tarda
varios minutos; el script espera a que termine.
VERIFICAR los endpoints contra la documentación vigente de la API de Environments antes del primer uso.
"""

from __future__ import annotations

import argparse
import glob
import os
import time

API = "https://api.fabric.microsoft.com/v1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", required=True, help="ruta o patrón del .whl")
    args = parser.parse_args()

    import requests
    from azure.identity import AzureCliCredential

    wheel = sorted(glob.glob(args.wheel))[-1]
    workspace, environment = os.environ["WS_ING_ID"], os.environ["ENV_FWK_ID"]
    token = AzureCliCredential().get_token("https://api.fabric.microsoft.com/.default").token
    cabeceras = {"Authorization": f"Bearer {token}"}
    base = f"{API}/workspaces/{workspace}/environments/{environment}"

    with open(wheel, "rb") as f:
        r = requests.post(f"{base}/staging/libraries", headers=cabeceras, files={"file": f}, timeout=300)
    r.raise_for_status()
    print(f"Subido {os.path.basename(wheel)}")

    r = requests.post(f"{base}/staging/publish", headers=cabeceras, timeout=60)
    r.raise_for_status()
    for _ in range(60):
        estado = requests.get(base, headers=cabeceras, timeout=60).json()
        situacion = estado.get("properties", {}).get("publishDetails", {}).get("state", "")
        print(f"  publicación: {situacion}")
        if situacion.lower() in ("success", "failed", "cancelled"):
            if situacion.lower() != "success":
                raise SystemExit(f"La publicación del Environment terminó en '{situacion}'")
            return
        time.sleep(20)
    raise SystemExit("La publicación del Environment no terminó en 20 minutos")


if __name__ == "__main__":
    main()
