# Automatización de migraciones de datos con agentes de IA

Este repositorio recoge el método que he construido para hacer migraciones de datos con agentes de IA (Claude Code). Trabajo en EVOTIC migrando los datos de clínicas estéticas y médicas desde su software de gestión antiguo a Flowww, un ERP en la nube para clínicas. Llevo **más de 60 migraciones desde 15 sistemas de origen distintos**.

Las primeras migraciones las hice a mano, de principio a fin (una de ellas está documentada en [migracion-datos-clinica-sqlserver-mysql](https://github.com/Giusebuompane/migracion-datos-clinica-sqlserver-mysql)). Cada una me enseñaba algo nuevo: un sistema de origen con sus trampas, un bug que no había visto o una regla de negocio que no estaba escrita en ningún sitio. A partir de esa experiencia convertí lo aprendido en documentación, prompts, skills y comprobaciones automáticas. Ahora un agente de IA sigue ese mismo método en cada migración nueva y yo me centro en revisar, decidir y validar.

En el repositorio no hay datos de clientes ni código interno de la empresa: las plantillas, los prompts, la skill y el validador son versiones genéricas que he reescrito a partir de mi trabajo real.

## La idea

Un agente de IA sin contexto comete los mismos errores que un compañero nuevo: asume formatos, inventa mapeos, carga sin comprobar. La solución no es escribirle un prompt más largo cada vez, sino darle **memoria del proyecto**: lo que ya se sabe del sistema de origen, las reglas que se aprendieron con errores reales y el estado de cada cliente.

```
                   ┌──────────────────────────────────────────┐
  Capa 0           │  Protocolo general                       │  reglas que aplican a TODAS las
                   │  (29 reglas aprendidas de errores reales)│  migraciones; se mantiene corto
                   └──────────────────────────────────────────┘
                   ┌──────────────────────────────────────────┐
  Capa 2           │  Conocimiento por sistema de origen      │  mapa de tablas, reglas fijas,
                   │  (15 sistemas: Cliniwin, Gesden, ...)    │  bugs conocidos y checklist
                   └──────────────────────────────────────────┘
                   ┌──────────────────────────────────────────┐
  Capa 1           │  Contexto de cada cliente                │  cifras reales, decisiones de
                   │  (una memoria por migración)             │  negocio, pendientes
                   └──────────────────────────────────────────┘
                   ┌──────────────────────────────────────────┐
  Capa 3           │  Guía del cargador compartido            │  lado destino: cómo se carga
                   │  (código común de carga a la BBDD)       │  cada tabla y sus fallos típicos
                   └──────────────────────────────────────────┘
```

Cada documento tiene un sitio fijo y una única fuente de verdad: si un bug es de un sistema de origen, vive en su Capa 2; si es del cargador común, en la Capa 3; solo si es una regla de proceso sube a la Capa 0. Así la documentación crece con cada migración sin duplicarse ni contradecirse.

## Cómo trabaja el agente y qué hago yo

| Fase | El agente | Yo |
|---|---|---|
| Arranque | Lee las 4 capas antes de tocar nada y me pregunta lo que falte | Le doy el cliente, el sistema de origen y la carpeta de trabajo, y relleno el `.env` con las credenciales (nunca van por el chat) |
| Análisis del origen | Explora el modelo, cuenta registros, busca los patrones ya conocidos de ese sistema | Confirmo con la clínica lo que no está claro |
| Mapeo | Propone el mapeo de campos y catálogos (servicios, profesionales, "¿cómo nos conoció?") | Reviso y confirmo cada mapeo |
| Extracción | Genera los scripts y los CSV en el formato de destino | Reviso los resúmenes y los casos raros |
| Validación | Ejecuta el validador automático y corrige cualquier FAIL | Reviso el informe |
| Carga | Prepara cada carga con backup previo y me pide confirmación antes de cada acción contra producción | Confirmo una a una |
| Cierre | Genera la batería de pruebas en Word con la tabla de cobertura origen/destino y actualiza la documentación de las 4 capas | Valido con la clínica en el sistema nuevo |

Cada migración tiene dos cargas reales: una carga inicial (POC) que la clínica revisa, y una carga final con un export nuevo, el día que deja el sistema antiguo. Los scripts se escriben pensando en esa segunda ejecución.

## Contenido del repositorio

```
.
├── plantillas/
│   ├── CLAUDE.md                     Instrucciones de proyecto para una sesión de migración
│   ├── capa0_protocolo.md            Protocolo general con una selección de reglas reales
│   ├── capa1_contexto_cliente.md     Memoria de una migración concreta
│   └── capa2_conocimiento_sistema.md Conocimiento de un sistema de origen (9 secciones fijas)
├── prompts/
│   └── prompt_arranque_migracion.md  Prompt de arranque de una sesión nueva
├── skills/
│   └── validar-migracion/SKILL.md    Skill con el procedimiento de validación antes y después de cargar
└── validador/
    └── validar_csv.py                Comprobaciones deterministas sobre los CSV antes de cargarlos
```

Para probar el validador sobre una carpeta de CSV:

```
pip install pandas
python validador/validar_csv.py <carpeta_csv>
```

Devuelve un informe con FAIL, WARN y OK por comprobación (IDs duplicados o con formato GUID, sexo desequilibrado, DNI sin letra, teléfonos mal compactados, clientes ficticios de bloqueo, agenda con fechas pasadas, descuentos fuera de rango, cabecera y línea de presupuesto intercambiadas, filas de clientes inexistentes, extensiones en mayúsculas y CSV con BOM). Termina con código 1 si hay algún FAIL, para que el agente no pueda pasar a la carga sin corregirlo.

## Algunas reglas que aprendí con errores reales

El protocolo real tiene 29 reglas; en `plantillas/capa0_protocolo.md` hay una selección reescrita en genérico. Estas son las que más tiempo me han ahorrado:

- **Las fechas ISO también se pueden estropear.** `pd.to_datetime(..., dayfirst=True)` intercambia día y mes sin dar error cuando los dos son menores o iguales a 12, aunque la fecha ya venga en formato `AAAA-MM-DD`. Lo detectó una clínica en producción. Ahora, antes de fijar el formato de una fecha, el agente tiene que mirar una muestra con día y mes ≤ 12.
- **Clientes ficticios que bloquean la agenda.** Muchas clínicas usan "clientes" llamados OCUPADO, VACACIONES o PRUEBA para bloquear huecos. En una migración eran el 16 % del historial y el 49 % de la agenda. Ahora se buscan siempre antes de dar los conteos por buenos.
- **Nunca cargar filas de clientes que no existen.** Presupuestos de pacientes creados después del export se cargaban con un ID que heredaría el siguiente cliente dado de alta. Ahora el cargador hace `JOIN` con la tabla de clientes y avisa de los excluidos.
- **Los valores por defecto esconden problemas.** Una función común asignaba sexo "F" a todo lo desconocido. El validador avisa si más del 85 % de los clientes tiene el mismo valor.
- **Los mapeos se construyen desde la consulta que los consume**, no desde todas las tablas donde aparece el dato. En un caso se pedían 120 servicios de más al implantador por no hacerlo así.

## Lo que he aprendido trabajando con agentes

- **Documentación frente a skills.** Un procedimiento que siempre se hace igual (validar, cerrar una carga) encaja en una skill. El conocimiento que crece con cada migración (bugs, cifras, decisiones) tiene que vivir en documentos que el agente lee y actualiza; dentro de una skill se quedaría congelado.
- **Subagentes con medida.** Para documentar de golpe 16 migraciones antiguas lancé varios agentes en paralelo y agoté el límite de uso de la sesión. Un solo agente trabajando de forma secuencial lo terminó sin problemas. Ahora reparto en paralelo solo lo que de verdad es independiente y ligero.
- **Confirmación antes de cada acción irreversible.** Los resets y las cargas masivas contra producción se ejecutan de una en una, con backup previo y mi confirmación explícita justo antes de cada una.
- **Lo que se puede comprobar con código no se deja a la memoria.** Los bugs que se repetían entre clientes acabaron en un validador automático que el agente ejecuta solo antes de cada carga.
- **El trabajo es de equipo.** Los prompts y la documentación los usan también mis compañeros en sus propias sesiones, y cada migración que se cierra deja actualizadas las 4 capas para la siguiente persona.

## Herramientas

Claude Code (sesiones de agente, subagentes, skills, instrucciones de proyecto), Python (pandas, SQLAlchemy, pyodbc, mysql-connector, python-dotenv), SQL Server, MySQL, Access, Google Cloud Storage y PowerShell.
