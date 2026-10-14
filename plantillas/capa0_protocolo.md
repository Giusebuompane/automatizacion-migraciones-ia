# Capa 0 — Protocolo general de migraciones

Reglas que aplican a todas las migraciones, sea cual sea el sistema de origen. Este documento se mantiene corto a propósito: el detalle de cada sistema vive en su Capa 2 y el de cada cliente en su Capa 1. Casi todas las reglas salieron de un error real; por eso cada una explica el motivo.

Esta es una selección, reescrita en genérico, del protocolo que uso en mi trabajo.

## Organización de la documentación

| Capa | Documento | Qué guarda |
|---|---|---|
| 0 | Este protocolo | Reglas de proceso comunes a todas las migraciones |
| 1 | `CONTEXTO_<Cliente>.md` | Estado, cifras y decisiones de una migración concreta |
| 2 | `conocimiento_<Sistema>.md` | Mapa de tablas, reglas fijas, bugs y checklist de un sistema de origen |
| 3 | Guía del cargador | Cómo se carga cada tabla en el destino y sus fallos típicos |

Cada hallazgo se documenta en una sola capa. Las demás enlazan a ella en vez de copiarlo.

## Ciclo de vida

1. **Dos cargas reales, siempre.** Una carga inicial (POC) que la clínica revisa en el sistema nuevo y una carga final con un export nuevo y completo, el día que deja el sistema antiguo. La carga final sustituye a la POC: se resetean las tablas de datos y se conservan las de mapeo y configuración.
2. **Los scripts se escriben para volver a ejecutarse** semanas o meses después contra otro export. Se conserva el código de la POC y se adapta, no se reescribe.
3. **Exports siempre completos**, nunca incrementales. Si llega uno incremental por error, se fusiona una vez como excepción.

## Extracción

4. **IDs crudos del origen en los CSV.** El mapeo a IDs del destino es trabajo de la carga. Un ID huérfano del origen sigue siendo un ID: se añade al fichero de mapeo con un nombre descriptivo, nunca se sustituye por un texto fijo.
5. **Los mapeos se construyen desde la consulta que los consume.** Un mismo servicio puede aparecer como texto libre (ya resuelto) y como ID estructurado (necesita mapeo). Solo el segundo entra en el fichero de mapeo.
6. **La IA propone, la persona confirma.** Cualquier mapeo de catálogos lo propone el agente con su recuento y lo confirma una persona antes de generar los CSV.
7. **Nada de valores por defecto que escondan problemas.** Un sexo desconocido se deja vacío, no se asume. Si más del 85 % de los clientes tiene el mismo valor, es una alarma.
8. **Fechas: mirar el dato antes de parsear.** `dayfirst=True` puede intercambiar día y mes en fechas que ya están en ISO cuando ambos son ≤ 12, sin ningún error. Antes de fijar el formato de un campo, revisar una muestra que tenga día y mes ≤ 12.
9. **Buscar clientes ficticios que bloquean agenda** (OCUPADO, BLOQUEO, PRUEBA, VACACIONES, CERRADO...) antes de dar por buenos los conteos. Pueden ser una parte enorme del historial.
10. **Fecha de alta cuando el origen no la trae:** la de origen; si falta, la de la primera cita del cliente; si tampoco hay, la del día de la carga. Se resuelve en la extracción y se informa de cuántos clientes van por cada vía.
11. **Teléfonos compactados:** si el cliente tiene algún teléfono, el primero nunca queda vacío.
12. **Texto: comprobar los bytes antes de "arreglar" acentos.** Una consola que muestra caracteres raros no significa que el dato esté mal.
13. **CSV en UTF-8 sin BOM**, con el separador que pida el destino, y columnas numéricas vacías a 0.
14. **Extensiones de fichero en minúsculas** en documentos y fotos: el destino falla al descargar `.PDF` o `.JPG`.

## Carga

15. **Backup antes de cualquier carga**, aunque no haya reset.
16. **Confirmación justo antes de cada acción irreversible** y una entidad cada vez, nunca el proceso completo de golpe.
17. **Nunca cargar filas cuyo cliente no exista** en la tabla de clientes del destino: heredarían el ID del siguiente cliente que se dé de alta. Tras cada carga, la consulta de huérfanos tiene que dar 0.
18. **Fotos y documentos sin fecha** se cargan con la fecha del día de la carga, y se avisa de cuántos son. No se deduce la fecha del nombre del fichero.

## Seguridad

19. **Credenciales siempre en un `.env` local**, que rellena la persona. Nunca en el chat, en un script, en la documentación ni en un log.
20. **El código común es de todos.** Un bug en una librería compartida afecta a todas las migraciones que la usan: se documenta en un solo sitio y se revisa en cada migración si ya está corregido.

## Cierre

21. **Batería de pruebas en Word** con la tabla de cobertura al principio (fichero de origen, tabla de destino, registros en origen, registros cargados, %, motivo si < 100 %) y una selección de clientes que entre todos cubran el 100 % de los conceptos migrados. Cualquier fila por debajo del 100 % necesita un motivo verificado.
22. **La documentación se actualiza al cerrar**, no al final del proyecto: Capa 1 siempre, Capa 2 si el hallazgo afecta al sistema, Capa 0 solo si es una regla de proceso nueva.
