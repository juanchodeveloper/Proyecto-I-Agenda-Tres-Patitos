# Proyecto I: Agenda Digital "Tres Patitos"

**Autor:** Juan Pablo Picado Salas  
**Curso:** Bases de Datos  
**Instituto Tecnológico de Costa Rica**

Este repositorio contiene la ampliación de la base de datos y de la aplicación de escritorio suministradas para el Proyecto I. Se conservaron el esquema y la arquitectura base, agregando tres módulos nuevos y las reglas de integridad necesarias.

## Módulos implementados

- Gestión de Ubicaciones - RF08, RF09 y RF10.
- Disponibilidad de Usuarios y Gestión de Tiempos - RF11 y RF12.
- Tareas Asociadas a Eventos - RF15, RF16 y RF17.

El módulo de Eventos Recurrentes (RF13-RF14) no fue seleccionado.

## Tecnologías

- PostgreSQL 18 o superior.
- Python 3.10 o superior.
- CustomTkinter.
- psycopg2-binary.
- tkcalendar.

## Estructura

```text
Proyecto-I-Agenda-Tres-Patitos/
├── agenda.py
├── script.sql
├── requirements.txt
├── README.md
├── docs/
│   ├── Informe_Proyecto_I_Agenda.pdf
│   ├── Informe_Proyecto_I_Agenda.docx
│   ├── Guia_Restauracion_Defensa.md
│   └── modelos/
└── pruebas/
    ├── datos_demo.sql
    ├── pruebas.sql
    └── validacion_integridad.sql
```

## Restauración de la base de datos

1. Crear una base de datos vacía llamada `agenda`.
2. Conectarse a `agenda`.
3. Ejecutar completamente `script.sql`.
4. Confirmar que se creó el esquema `prototipo`.
5. Instalar las dependencias de Python:

```bash
pip install -r requirements.txt
```

6. Revisar el bloque `DB_CONFIG` al inicio de `agenda.py` y ajustar usuario, contraseña, host o puerto si el equipo utiliza valores diferentes.
7. Ejecutar la aplicación:

```bash
python agenda.py
```

## Pruebas

`pruebas/datos_demo.sql` carga datos sencillos para demostrar los módulos. `pruebas/pruebas.sql` contiene casos positivos, negativos y de límite. `pruebas/validacion_integridad.sql` comprueba de forma controlada RE04 y RE05.

La versión final fue restaurada y probada con PostgreSQL 18.4. También se verificaron la conexión de la aplicación, los CRUD de los módulos seleccionados, los reportes, la prevención de traslapes y las reglas de integridad principales.

## Documentación

El informe final incluye la matriz de trazabilidad, los modelos y las capturas reales utilizadas como evidencia. Los archivos de documentación se encuentran en la carpeta `docs`.
