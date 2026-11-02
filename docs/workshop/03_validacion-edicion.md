# Validación de esta edición

Fecha: 2 de noviembre de 2026. Base del framework: `f0f2551`, biblioteca `0.2.0`.

## Alcance

Esta edición conserva los 162 archivos versionados distintos del README sin cambios respecto al origen.
El README original está íntegro en `README-framework.md`; las diferencias son documentación para su público.
No se cambian contratos, código, tests, esquemas ni items Fabric.
Los dos repositorios locales conservan el historial y no tienen remoto de publicación.

## Comprobaciones realizadas

- Enlaces locales y referencias a scripts/tests existentes.
- Sintaxis de bloques PowerShell, Python (también los incrustados en PowerShell) y YAML.
- Generación de un producto completo desde esta edición: ocho IDs Fabric renovados, contratos y reglas válidos.
- `git diff --check` correcto.
- Suite completa `pytest --delta`: **80 pruebas correctas**, usando una carpeta temporal propia.
- Revisión de la checklist del framework: cambio exclusivamente documental, sin nuevas tablas, KPIs o transformaciones.

La primera ejecución de pytest encontró acceso denegado al directorio temporal anterior del usuario.
Se repitió con `--basetemp .herramientas/pytest-secuencial-20261102`, sin cambiar los tests. La ejecución final se hizo de forma secuencial.
Las trazas de diagnóstico emitidas al superar 90 segundos no son fallos: la suite terminó con 80 pruebas correctas.

## Pre-commit: dos controles pendientes por el equipo

Se ejecutó `pre-commit run --all-files`. Ruff, mypy, reglas del framework, contratos, catálogo, YAML/esquemas,
SQL, workflows y Terraform pasaron. Se corrigió el PATH de Git Bash para Terraform.
**No está completamente en verde:** Windows Control de aplicaciones bloqueó los ejecutables de:

- `check-merge-conflict`.
- `gitleaks`.

Ambos devolvieron `WinError 4551`. No se desactivaron hooks ni se añadieron excepciones.
El administrador del equipo debe resolver el bloqueo o repetir la validación en el devcontainer preparado.
La comprobación manual de documentos no sustituye esos controles.

## Reproducción y límites

Seguir la guía de preparación para instalar las herramientas en otro equipo.
El entorno virtual y las herramientas usadas para esta verificación se reutilizaron desde la plantilla original
y no forman parte de la distribución Git.

Logs locales, excluidos por Git: `.herramientas/pre-commit-edicion.log` y
`.herramientas/pytest-edicion-corregido.log`.

No se ejecutaron los comandos cloud o las mutaciones SQL de las guías.
Conectividad SQL/OneLake, runtime Fabric, permisos, pipelines y consumo Power BI requieren el ensayo del instructor.
BPA/Fab Inspector no se ejecutaron: no se modificaron artefactos de analítica.
