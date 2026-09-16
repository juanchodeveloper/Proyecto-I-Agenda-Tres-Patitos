# Guía de restauración y defensa

**Autor:** Juan Pablo Picado Salas  
**Proyecto:** Agenda Digital "Tres Patitos"

## 1. Restauración

1. Crear una base de datos vacía llamada `agenda`.
2. Conectarse a esa base en DBeaver o psql.
3. Ejecutar `script.sql` completo.
4. Confirmar el esquema `prototipo` y las tablas principales.
5. Si se necesitan datos rápidos para una demostración, ejecutar `pruebas/datos_demo.sql`.

La restauración final fue comprobada con PostgreSQL 18.4. El esquema quedó con 11 tablas, 5 vistas, 4 funciones y 3 triggers.

## 2. Ejecución de Python

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Revisar `DB_CONFIG` en `agenda.py`.
3. Ejecutar:

```bash
python agenda.py
```

4. Presionar **Recargar datos** y comprobar las pestañas Usuarios, Categorías, Eventos, Ubicaciones, Disponibilidad y Tareas.

## 3. Recorrido recomendado para la defensa

1. **Ubicaciones (RF08):** crear o modificar una ubicación.
2. **Eventos y ubicaciones (RF09):** mostrar un evento asociado a una ubicación e intentar crear otro en un horario traslapado para explicar el trigger de rechazo.
3. **Ranking y agenda (RF09-RF10):** mostrar el histórico/agenda por recinto y el ranking de uso.
4. **Disponibilidad (RF11-RF12):** registrar una franja y buscar usuarios libres para un rango de horas.
5. **Tareas (RF15-RF17):** crear o actualizar una tarea y mostrar vencimientos y carga de trabajo.
6. Si se solicita integridad adicional, ejecutar `pruebas/validacion_integridad.sql` para demostrar RE04 y RE05.

## 4. Puntos técnicos para explicar

- Los traslapes se controlan en PostgreSQL para que la regla se cumpla aunque el dato no venga de la GUI.
- El propietario de un evento debe estar activo.
- La jerarquía de categorías no permite ciclos directos ni indirectos.
- RF12 cruza las franjas registradas con los compromisos de eventos del usuario.
- Los reportes de tareas se implementan mediante vistas para mantener las consultas simples desde Python.
- `rollback()` evita dejar una transacción incompleta cuando una operación produce un error.
- `SET search_path TO prototipo, public` permite trabajar con los objetos del esquema sin anteponer `prototipo.` en cada consulta.
