# Proyecto I - Agenda Digital "Tres Patitos"

Ampliación de una base de datos existente y de su aplicación de escritorio para el curso de Bases de Datos.

## Módulos seleccionados

Se implementaron tres de los cuatro módulos propuestos:

1. **Gestión de Ubicaciones** — RF08, RF09 y RF10.
2. **Disponibilidad de Usuarios y Gestión de Tiempos** — RF11 y RF12.
3. **Tareas Asociadas a Eventos** — RF15, RF16 y RF17.

El módulo de **Eventos Recurrentes (RF13-RF14)** no fue seleccionado.

## Tecnologías

- PostgreSQL 18 o superior.
- Python 3.10 o superior.
- `psycopg2-binary`.
- `customtkinter`.
- `tkcalendar`.
- `tkinter` / `ttk`.

## Estructura principal

```text
Proyecto-I-Agenda-Tres-Patitos/
├── agenda.py
├── script.sql
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
│   ├── INFORME_TECNICO_PROYECTO_1.docx
│   ├── PROCEDIMIENTO_RESTAURACION_Y_DEFENSA.md
│   └── modelos/
├── pruebas/
│   ├── pruebas.sql
│   └── README.md
└── evidencias/
    └── README.md
```

## Restauración y ejecución

1. Crear una base de datos vacía llamada `agenda`.
2. Conectarse a esa base de datos.
3. Ejecutar completamente `script.sql`.
4. Confirmar la creación del esquema `prototipo` y sus objetos.
5. Ajustar el bloque `DB_CONFIG` de `agenda.py` según la instalación local.
6. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

7. Ejecutar la aplicación:

```bash
python agenda.py
```

## Configuración de conexión

La aplicación centraliza la conexión en `DB_CONFIG` dentro de `agenda.py`. No se debe publicar una contraseña personal real en el repositorio.

## Estado de validación

- `agenda.py`: revisado sintácticamente.
- Modelos, SQL y correspondencia SQL-Python: revisados estáticamente.
- Restauración completa en PostgreSQL, pruebas funcionales de GUI y evidencias: pendientes de ejecución local antes de cerrar la entrega.

## Control de versiones

El repositorio se actualizará mediante commits reales y progresivos conforme se realicen la restauración, pruebas, correcciones y documentación final del proyecto.
