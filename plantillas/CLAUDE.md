# Instrucciones de proyecto: migración de [CLIENTE] desde [SISTEMA ORIGEN]

Este fichero va en la raíz de la carpeta de trabajo de la migración. El agente lo lee al empezar cada sesión.

## Antes de tocar nada

1. Lee, en este orden:
   - `capa0_protocolo.md`: reglas que aplican a todas las migraciones.
   - `conocimiento_[SISTEMA].md` (Capa 2): mapa de tablas, reglas fijas y bugs conocidos del sistema de origen.
   - `CONTEXTO_[CLIENTE].md` (Capa 1), si ya existe: estado real de esta migración, decisiones tomadas y pendientes.
   - La guía del cargador (Capa 3), antes de ejecutar cualquier carga.
2. Si el sistema de origen no tiene documento de Capa 2, es un sistema nuevo: avísame y crea el documento al cerrar la migración con las 9 secciones de la plantilla.
3. Confirma conmigo el estado real antes de asumir que algo pendiente ya se resolvió.

## Carpeta de trabajo

- Trabaja solo dentro de esta carpeta. No reutilices rutas, scripts ni CSV de otra migración sin decírmelo.
- Estructura: `Origen/` (export recibido, solo lectura), `Python/` (scripts de extracción), `Destino/` (CSV finales), `CARGA/` (cargador y logs), `backup/`.

## Credenciales

- Las credenciales de cualquier base de datos van en un `.env` en la raíz de la carpeta. Lo relleno yo editando el fichero.
- Nunca me pidas usuario ni contraseña por el chat, nunca los escribas en un script, en un `.md` o en un log, y nunca muestres el contenido del `.env`. Para comprobarlo, enséñame solo qué claves tienen valor.

## Reglas de trabajo

- La extracción lleva los IDs crudos del origen. Los IDs del destino se resuelven en la carga, con las tablas de mapeo.
- Cualquier mapeo de catálogos (servicios, productos, profesionales, origen del cliente) lo propones tú y lo confirmo yo antes de generar los CSV.
- Al generar los CSV, ejecuta el validador (`validador/validar_csv.py`). Cualquier FAIL se resuelve antes de pasar a la carga.
- Antes de cada acción contra la base de datos de producción (reset, carga masiva, subida de ficheros): backup de las tablas afectadas y pregunta directa justo antes. Una entidad cada vez.
- En la consola usa solo ASCII; los ficheros, siempre en UTF-8.

## Al cerrar

- Genera la batería de pruebas en Word con la tabla de cobertura (origen, destino, registros en origen, registros cargados, %, motivo si < 100 %) y los clientes de prueba.
- Actualiza `CONTEXTO_[CLIENTE].md` con el estado, las cifras y las decisiones de esta sesión.
- Si has encontrado algo que afecta a cualquier cliente de este sistema, añádelo a su Capa 2. Si es una regla de proceso nueva, propónmela para la Capa 0.
