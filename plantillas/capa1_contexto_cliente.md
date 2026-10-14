# CONTEXTO — [Cliente] ([identificador])

Memoria de una migración concreta. La lee el agente al retomar el trabajo y la actualiza al cerrar cada sesión. Tiene que bastar para que cualquier persona, o una sesión nueva del agente, sepa dónde estamos sin preguntar.

## 1. Resumen ejecutivo

- **Sistema de origen:** [nombre, versión, tipo de export recibido y fecha]
- **Tipo de clínica y centros:** [estética / dental / médica · nº de centros]
- **Estado:** [análisis / extracción / POC cargada / validada por el cliente / carga final hecha / cerrada]
- **Próximo paso:** [qué falta y quién lo tiene]

## 2. Alcance acordado

| Concepto | ¿Se migra? | Notas |
|---|---|---|
| Clientes | | |
| Historial clínico / notas | | |
| Agenda futura | | |
| Presupuestos | | |
| Bonos y stock | | |
| Documentos y fotos | | |

## 3. Lógica de negocio de este cliente

Reglas que solo aplican aquí y por qué (decisiones del cliente o del implantador, con fecha).

## 4. Mapeos

Dónde están los ficheros de mapeo, quién los validó y cuándo. Excepciones conocidas.

## 5. Cifras reales

| Tabla de destino | Registros en origen | Registros cargados | % | Motivo si < 100 % |
|---|---|---|---|---|
| | | | | |

## 6. Bugs y hallazgos de esta migración

Cada uno con su evidencia y dónde se documentó si afecta a más clientes (Capa 2 o Capa 3).

## 7. Pendientes

- [ ] [pendiente] — [responsable] — [fecha]

## 8. Historial de sesiones

- [AAAA-MM-DD] — [qué se hizo, qué se decidió]
