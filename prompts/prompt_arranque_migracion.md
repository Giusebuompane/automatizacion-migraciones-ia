# Prompt de arranque de una migración

Se pega al abrir una sesión nueva del agente, siempre una sesión por cliente, con el directorio de trabajo en la carpeta de ese cliente. Rellenar los campos entre corchetes. Las contraseñas nunca van aquí.

---

Voy a empezar (o retomar) una migración. Datos que ya tengo:

- Cliente: [nombre]
- Sistema de origen: [nombre / "no lo sé"]
- Carpeta de trabajo: [ruta completa]
- Tipo de clínica y nº de centros: [estética / dental / médica · nº]
- Export recibido: [completo / parcial] · ¿incluye agenda futura?: [sí / no]
- Datos no secretos del destino, si ya los tengo: [host · base de datos]
- Contexto que ya conozco: [qué no se migra, reglas del cliente...]

0. **Credenciales.** Antes de nada, crea el `.env` en la raíz de la carpeta a partir de `.env.example` y dime la ruta. Lo relleno yo. No conectes a ninguna base de datos hasta que te confirme que está listo. Nunca me pidas credenciales por el chat ni muestres el contenido del `.env`.

1. **Lee la documentación en este orden** antes de analizar nada: protocolo general (Capa 0), conocimiento del sistema de origen (Capa 2) y contexto del cliente (Capa 1) si existe. Si el sistema no tiene Capa 2, dímelo: es un sistema nuevo y habrá que documentarlo al cerrar.

2. **Analiza el origen** y dame un resumen: tablas o ficheros, recuento de registros, claves, rango de fechas y cualquier patrón conocido de la Capa 2 que aparezca (o que no aparezca y debería).

3. **Propón el alcance** concepto por concepto (clientes, historial, agenda futura, presupuestos, bonos, documentos y fotos) y espera a que lo confirme.

4. **Propón los mapeos de catálogos** con el recuento de cada valor de origen y la opción de destino que propones. Marca los que no tienen equivalente. No generes los CSV hasta que los confirme.

5. **Antes de fijar el formato de cualquier fecha**, enséñame una muestra con día y mes ≤ 12. **Busca clientes ficticios** de bloqueo de agenda y dime cuántas citas tienen.

6. **Genera los scripts de extracción y los CSV** pensando en que se volverán a ejecutar con un export nuevo para la carga final.

7. **Ejecuta el validador** sobre la carpeta de CSV y enséñame el informe. Cualquier FAIL se corrige antes de seguir.

8. **Al terminar la sesión**, actualiza el contexto del cliente (Capa 1) con el estado, las cifras y las decisiones, y dime si hay algo que deba subir a la Capa 2 o a la Capa 0.
