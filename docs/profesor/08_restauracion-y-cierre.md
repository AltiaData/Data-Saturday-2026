# Restauración y cierre

Minutos 235–240 (5 min). Guía del alumnado: [Restauración y cierre](../workshop/02_seguir-las-demos.md).
Sin rama propia: se ejecuta sobre el estado que deja la demo 6 (`alumno-99/demo-07` en el repositorio).

> **No ensayada.** Lo que sigue procede de la guía del alumnado y de la preparación del profesorado; los resultados
> son los esperados, no los observados. El laboratorio del ensayo no se ha restaurado.

## Objetivo y mensajes clave

- Restaurar el origen no borra nada: se observa una versión nueva. No se pierde auditoría ni historia.
- Restaurar no significa limpiar los defectos naturales del volcado: bajo Q4 siguen existiendo rechazos.
- La cuarentena conserva la evidencia histórica.
- Para otro ensayo desde cero hacen falta una copia greenfield y workspaces vacíos: `restaurar` no reinicia marcas ni
  borra estado Delta.

## Qué enseñar en pantalla

- La historia de `C0001` en `lh_gold` tras restaurar: cuarta versión en Sevilla.
- `fwk_cuarentena` agrupada por lote y versión: la evidencia anterior sigue ahí.

## Comandos

```powershell
& $Python -m scripts.modificar_csv restaurar
& $Python -m scripts.laboratorio datos --env-file .env.alumno
Start-Sleep -Seconds 6
```

Fabric:

1. Bronze → silver → gold CRM con el lote nuevo `crm-restaurar`.
2. Bronze → silver devoluciones con `dev-restaurar`.
3. Revalidación con `dev-restaurar-q4`.

## Resultado esperado

- `C0001` vuelve a Sevilla y abre una cuarta versión; no se borra historia.
- Devoluciones bajo Q4: **362 válidas y 35 rechazos** naturales.

## Tiempo medido

No ensayada. Estimación del plan: unas 6 ejecuciones, 12–15 min. **No cabe en 5 minutos.** La guía propone iniciar
la publicación al comenzar el último bloque y, si Fabric tarda, registrar los lotes pendientes y terminar su
comprobación antes de cerrar el laboratorio. El recorte está pendiente de decisión (opción E de la
[chuleta](00_chuleta-del-dia.md#si-se-va-con-retraso-opciones-decisión-pendiente)).

## Preguntas frecuentes previsibles

- **¿Por qué no se borra la historia de Barcelona y Valencia?** Fueron observaciones reales; SCD2 las conserva y la
  vuelta a Sevilla es otra observación.
- **¿Por qué siguen 35 rechazos tras restaurar?** Son defectos del volcado original que Q4 sigue rechazando; restaurar
  solo deshace los cuatro defectos sembrados.
- **¿Cómo dejo el laboratorio como al principio?** No se puede con `restaurar`: hace falta otro producto y workspaces
  vacíos.

## Incidencias previsibles

No hay incidencias del diario porque no se ensayó. Por analogía con las demos 4 y 5 (no comprobado aquí): esperar 6 s
tras publicar el CSV antes del lote CRM, una sesión de Spark cada vez y **Refresh** en el endpoint.

## Plan B

El diario no define dependencias para la restauración. Por lo que hace, necesita la historia SCD2 de la demo 5 (para
abrir la cuarta versión) y el contrato Q4 de la demo 3 (para revalidar). Quien no haya llegado a la demo 5 en su
laboratorio no puede reproducir el resultado de CRM en el tiempo del bloque: mostrarlo en la pantalla del profesorado.

## Cierre

- Recordar la [preparación](../workshop/01_antes-de-la-sesion.md) para repetir el taller en casa con un producto nuevo.
- Recordar que las ramas `alumno-99/demo-NN` permiten retomar cualquier demo (plan B del [README](README.md)).
- Pedir al alumnado que pare las sesiones de Spark y, si su capacidad es de pago, que la pause.
