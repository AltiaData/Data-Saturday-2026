# Validación de la edición CSV · 2 de noviembre de 2026

Framework 0.3.0, basado en la revisión f0f2551 y los cambios locales de esta entrega. Las copias del instructor y del
alumno comparten código, scripts, schemas, tests y datos; difieren en su portada y en la configuración privada local.
No se han publicado nuevos repositorios ni se ha hecho push de esta actualización.

## Evidencia realizada

- Exportación **real y de solo lectura** desde Azure SQL y Cosmos: 49 tablas/41.454 filas y diez contenedores/18.665 documentos.
- Verificación de SHA-256, recuentos por parte y documento JSON/ID en todo el paquete, también después de copiarlo.
- Greenfield real: destino nuevo, exclusión de dotenv privados y CSV mutables, ejemplo del alumno incluido.
- Activación secuencial de base, incremental, Q2, Q3, Q4 y SCD2; validación de contratos/referencias y JSON Schema.
- Suite completa local Spark/Delta: **88 pruebas correctas** en 724,93 segundos.
- Después, diez pruebas específicas de configuración, greenfield y publicación de librería volvieron a pasar tras
  los ajustes finales; una prueba adicional con Spark y el CSV real valida **387/10 en Q1 y 358/39 en Q2**.
  En total, 89 tests distintos comprobados; no se ha repetido tres veces la misma suite en copias idénticas.
- El caso Delta de CSV cubre completa → incremental, origen modificado entre reintentos y lote vacío sin perder silver.
- Wheel `datafwk-0.3.0-py3-none-any.whl` construido correctamente.
- Sintaxis de scripts, enlaces y guía; revisión del diff y checklist del framework.

La suite completa se ejecutó con Java 17, Spark 3.5 y Delta 3.3.2, usando una carpeta temporal propia.
El primer arranque de Spark bajo restricciones locales no avanzó; se detuvo y se repitió con los permisos de ejecución
necesarios. Los volcados de pila de diagnóstico a los 90 segundos no son errores de test.

## Checks pendientes por el equipo

Se ejecutó `pre-commit run --all-files`. Ruff, mypy, reglas FW, contratos, catálogo, YAML/JSON Schema, SQL, workflows,
Terraform y límite de tamaño de ficheros pasaron. Windows Control de aplicaciones bloquea `check-merge-conflict`
y `gitleaks` con `WinError 4551`. No se han desactivado hooks ni eludido la directiva. Por tanto, el requisito de
pre-commit completamente verde sigue pendiente de ejecutar ambos en un equipo autorizado o CI.

El exportador contiene **dos excepciones Ruff justificadas en la misma línea**: S608 para SELECT con identificadores
obtenidos del catálogo, delimitados y escapados; S603 para Azure CLI localizado y argumentos separados, sin shell.
No se silencian otras reglas. El escaneo completo de secretos no se considera sustituido por comprobar `.gitignore`.

## Checklist y límites

Las nuevas transformaciones puras tienen tests; la lógica sigue en `src/datafwk`. No se añaden tablas ni KPIs ni se
modifican los contratos versionados existentes. Los cambios contractuales Q1–Q4 y tipo1→SCD2 son pasos explícitos del
laboratorio. El ADR 0003 documenta el origen CSV y la modalidad de Fabric propio.

No se ha desplegado esta entrega en una capacidad Fabric ni se han creado cuentas/bases del laboratorio.
Falta el ensayo remoto del instructor: permisos, asignación de capacidad, runtime, Environment, OneLake y notebooks.
Las contraseñas del fichero privado son valores propuestos por crear, no credenciales de usuarios ya provisionados.
No se tocaron artefactos de analítica; BPA/Fab Inspector no aplica a este cambio.

Los logs locales de la plantilla están en `.herramientas/pytest-csv-completo.log`, `pytest-csv-real.log`,
`precommit-csv.log` y `exportacion.log`. No se distribuyen logs, virtualenv ni herramientas locales.
