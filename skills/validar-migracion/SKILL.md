---
name: validar-migracion
description: Valida una migración de datos antes y después de cargarla en el destino. Úsala cuando haya CSV finales listos para cargar, después de cada carga, o cuando el usuario pida comprobar o cerrar una migración.
---

# Validar una migración

Procedimiento fijo de validación. No sustituye a la revisión de la persona: es un primer filtro que se ejecuta siempre igual. El conocimiento que cambia con cada cliente (bugs, cifras, decisiones) no va aquí, va en la documentación de Capa 1 y Capa 2.

## Antes de cargar

1. Ejecuta el validador sobre la carpeta de CSV finales:
   ```
   python validador/validar_csv.py <carpeta_csv>
   ```
2. Enseña el informe completo al usuario, agrupado por FAIL, WARN y OK.
3. Cualquier FAIL se corrige en el script de extracción (no editando el CSV a mano) y se vuelve a ejecutar el validador.
4. Para cada WARN, explica si es un problema real o un dato correcto del origen, con una muestra de filas como evidencia.
5. Comprueba además lo que el validador no puede ver porque necesita el origen:
   - Recuento de registros de cada CSV frente a su tabla o fichero de origen, después de los filtros de negocio acordados.
   - Totales de importes (presupuestos, pagos, deudas) frente al origen.
   - Formato real de cada campo de fecha con una muestra de día y mes ≤ 12.

## Después de cada carga

1. Recuento de filas cargadas por tabla frente a los CSV.
2. Filas huérfanas: cualquier tabla que referencie clientes tiene que dar 0 en
   ```sql
   SELECT COUNT(*) FROM <tabla> t
   LEFT JOIN clients c ON c.ClientID = t.<campo_cliente>
   WHERE c.ClientID IS NULL;
   ```
3. Documentos y fotos sin fecha o sin ruta: tiene que dar 0.
4. Si algún recuento no cuadra, no lo des por bueno: busca el motivo y enséñaselo al usuario.

## Al cerrar

1. Construye la tabla de cobertura: fichero de origen, tabla de destino, registros en origen, registros cargados, %, motivo si < 100 %. Ninguna fila por debajo del 100 % puede quedar sin un motivo verificado.
2. Elige clientes de prueba que entre todos cubran el 100 % de los conceptos migrados, con al menos un caso especial (baja, exclusión, historial muy largo).
3. Genera la batería de pruebas en Word con la tabla de cobertura y una tabla por cliente: concepto, qué verificar en el destino, dato esperado y fichero de origen.
4. Actualiza el contexto del cliente (Capa 1) con las cifras finales.
