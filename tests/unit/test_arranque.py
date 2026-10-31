from pathlib import Path

from datafwk.arranque import cargar_contexto, raiz_configuracion

REPO = Path(__file__).resolve().parents[2]


def test_raiz_configuracion_en_onelake():
    assert raiz_configuracion("proyecto-datos-test") == (
        "abfss://proyecto-datos-test@onelake.dfs.fabric.microsoft.com/lh_bronze.Lakehouse/Files/_framework"
    )


def test_contexto_desde_la_configuracion_del_repo():
    ctx = cargar_contexto("dev", "proyecto-datos-dev", "ventas", raiz=str(REPO))
    assert ctx.entorno.nombre == "dev"
    assert set(ctx.fuentes) == {"pedidos", "clientes"}
    contrato = ctx.contrato("pedidos")
    assert contrato.clave == ("id_pedido",)
    assert contrato.politica_rechazo == "cuarentena"
