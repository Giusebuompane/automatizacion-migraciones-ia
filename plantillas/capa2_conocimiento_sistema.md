# Conocimiento — [Sistema de origen]

Conocimiento generalizado de un sistema de origen: aplica a cualquier cliente futuro que venga de este mismo software. Lo que es propio de un solo cliente va en su Capa 1. Todos los documentos de Capa 2 tienen estas 9 secciones, en este orden, para que el agente sepa dónde buscar.

## 1. Qué es [Sistema]

Tipo de software, motor de base de datos, formatos de export que se han visto y en qué se diferencian.

## 2. Clientes migrados desde [Sistema]

| Cliente | Identificador | Estado | Contexto (Capa 1) |
|---|---|---|---|
| | | | |

## 3. Mapa de tablas y ficheros de origen

| Tabla o fichero de origen | Contenido | Destino |
|---|---|---|
| | | |

Claves primarias, relaciones y cualquier particularidad (por ejemplo, GUID como clave en vez de un número, o datos calculados con procedimientos almacenados que hay que persistir antes de extraer).

## 4. Reglas fijas confirmadas

Reglas que se han cumplido en todos los clientes de este sistema, con la fecha y el cliente donde se confirmaron.

## 5. Alcance variable y particularidades

Lo que cambia de un cliente a otro (por tipo de clínica, versión del software, módulos contratados) y hay que preguntar siempre.

## 6. Bugs reales encontrados (con evidencia)

Agrupados por tabla. Cada uno con el síntoma, la causa, el arreglo y el cliente donde apareció.

## 7. Incidencias y pendientes abiertos

Lo que no está resuelto y a qué clientes puede afectar.

## 8. Precedentes de código reutilizable

Qué scripts o consultas de migraciones anteriores sirven como punto de partida y qué hay que adaptar.

## 9. Antes de arrancar una migración de [Sistema] — checklist rápida

- [ ] Identificar la variante del export.
- [ ] Comprobar las claves primarias y si son estables entre exports.
- [ ] Revisar las reglas fijas de la sección 4 y los bugs de la sección 6.
- [ ] Buscar clientes ficticios de bloqueo de agenda.
- [ ] Revisar el formato real de cada campo de fecha.
