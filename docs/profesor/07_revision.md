# Demo 7 · Revisión del cambio

Minutos 220–235 (15 min). Guía del alumnado: [Demo 7](../workshop/02_seguir-las-demos.md).
Rama de punto inicial: `alumno-99/demo-07`.

## Objetivo y mensajes clave

- El contrato es una API: aprobar un cambio exige evidencia de reglas, catálogo, pruebas y operación.
- Los secretos y los CSV mutables quedan fuera de Git (`.env.alumno`, `data/laboratorio/`).
- Un `git diff` vacío no implica ausencia de cambios: en un greenfield sin commit hay que revisar también los ficheros
  no seguidos.
- No se silencian reglas para conseguir verde. Una limitación de herramientas se registra y se completa en CI.

## Qué enseñar en pantalla

- `git status --short` en el proyecto greenfield: contratos Q4 y SCD2 y configuración incremental pendientes de
  revisión.
- `docs/catalogo.md` regenerado (no se edita a mano).
- Sobre las ramas, el cambio acumulado del taller:
  `git diff --stat alumno-99/demo-02 alumno-99/demo-07 -- contracts config`.
- La salida de `pre-commit`, con los tres hooks de Terraform en código 127 y el resto en verde.

## Comandos

```powershell
& $Python scripts/generar_catalogo.py
& $Python scripts/validar_contratos.py
& $Python scripts/agente_lint.py config/fuentes/crm.yml contracts/silver/lineas_devolucion.yml
git status --short
git check-ignore .env.alumno data/laboratorio/clientes_crm.csv
& $Python -m pytest
pre-commit run --all-files
$env:SKIP='terraform_fmt,terraform_validate,terraform_tflint'; pre-commit run --all-files
```

## Resultado esperado

- `generar_catalogo`, `validar_contratos` y `agente_lint` correctos.
- `git check-ignore` lista `.env.alumno` y el CSV de `data/laboratorio`: ambos ignorados.
- `pytest` sin Java: 73 correctos y 17 omitidos (los de Spark, con motivo). Con Java 17, añadir `--delta`.
- `pre-commit run --all-files`: todo en verde salvo los tres hooks de Terraform, que fallan con código 127 sin
  Terraform ni tflint (vienen en el devcontainer).

## Tiempo medido

`pytest` 20 s. `pre-commit run --all-files` varios minutos la primera vez, porque instala los entornos de los hooks.
Margen **holgado** si los hooks ya están instalados; si no, conviene haber pedido en la preparación que se ejecute una
vez.

## Preguntas frecuentes previsibles

- **¿Por qué se permite `SKIP` si no se silencian reglas?** No se desactiva una regla: falta la herramienta en el equipo
  local. Se registra, se limita a esos tres hooks y la validación completa se hace en CI.
- **¿Por qué se omiten tests?** Los de Spark necesitan Java; sin él se omiten con motivo y en CI se ejecutan.
- **¿Por qué `docs/catalogo.md` aparece en el diff?** Se regenera a partir de los contratos; si un contrato cambia, el
  catálogo también, y el hook `catalogo-actualizado` lo comprueba.

## Incidencias reales del diario

- Hallazgo 33 (corregido): en Windows el catálogo se escribía con CRLF y `git status` lo marcaba modificado sin cambios.
- Hallazgo 34 (corregido): sin Java, `pytest` daba 14 errores `JAVA_GATEWAY_EXITED`; ahora se omiten con motivo.
- Hallazgo 35 (corregido): la guía no decía qué hacer con los hooks de Terraform; ahora explica el `SKIP`.
- Hallazgo 23 (corregido): sin la corrección del YAML generado, `yamllint` fallaría en esta demo.
- Hallazgo 36 (pendiente): `03_validacion-edicion.md` aún no recoge que `pre-commit` está en verde salvo Terraform.

## Plan B

Solo repositorio: no necesita Fabric ni lotes previos. Procedimiento común en el
[README](README.md#plan-b-común-incorporarse-en-la-demo-nn).

```powershell
Set-Location $Plantilla
git switch alumno-99/demo-07
```

En la rama los contratos ya están confirmados, así que `git status` no muestra cambios: para enseñar la revisión,
usar el diff entre ramas indicado arriba. `git check-ignore` funciona aunque `data/laboratorio/` no exista.
