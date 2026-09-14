# Procedimiento de restauración y ejecución para la defensa

## Antes de la defensa

1. Confirmar PostgreSQL 18+ y Python 3.10+.
2. Confirmar acceso a `script.sql`, `agenda.py` y al repositorio público.
3. Instalar las dependencias con `pip install -r requirements.txt`.
4. Saber el usuario, contraseña, host y puerto de PostgreSQL de la máquina.
5. No usar una contraseña personal real dentro del repositorio.

## Etapa 1 - Restauración limpia

1. Crear una base de datos vacía llamada `agenda`.
2. Conectarse a `agenda`.
3. Ejecutar el `script.sql` completo.
4. Refrescar el árbol de objetos.
5. Confirmar el esquema `prototipo`.
6. Confirmar las tablas nuevas: `ubicaciones`, `tipos_disponibilidad`, `disponibilidades`, `tareas`.
7. Confirmar las vistas principales: `vista_ocupacion_ubicaciones`, `vista_eventos_tareas_vencidas`, `vista_carga_trabajo`.
8. Confirmar las funciones: `evitar_ciclo_categorias`, `validar_propietario_activo`, `evitar_traslape_ubicacion`, `usuarios_disponibles`.
9. Si el script produce un error, detenerse y corregirlo antes de abrir la GUI.

## Etapa 2 - Puesta en marcha

1. Abrir `agenda.py`.
2. Ajustar únicamente `DB_CONFIG` si el entorno usa otras credenciales o puerto.
3. Ejecutar `python agenda.py`.
4. Confirmar las pestañas: Usuarios, Categorías, Eventos, Ubicaciones, Disponibilidad y Tareas.
5. Presionar **Recargar datos** y verificar que no aparezcan errores de conexión o estructura.

## Etapa 3 - Demostración recomendada

1. Crear una ubicación (RF08).
2. Crear un evento con descripción y ubicación (RF04, RF09).
3. Intentar crear otro evento que se traslape en el mismo recinto y explicar el rechazo (RF09).
4. Mostrar el ranking y la agenda por ubicación (RF09-RF10).
5. Crear una franja de disponibilidad y ejecutar la búsqueda de usuarios libres (RF11-RF12).
6. Crear una tarea, modificar su estado y mostrar los reportes de vencimientos y carga (RF15-RF17).
7. Si el profesor solicita integridad del sistema base, demostrar RE04 o RE05 con una prueba controlada.

## Prueba de límites fácil de explicar

Para RF09, un evento de 09:00 a 10:00 y otro de 10:00 a 11:00 en el mismo recinto **sí pueden coexistir**. Los intervalos se tratan como `[inicio, fin)`, por lo que solo hay traslape si:

```text
inicio1 < fin2  y  inicio2 < fin1
```

## Qué no afirmar sin comprobar

- No decir que el script restaura sin errores hasta ejecutarlo realmente en PostgreSQL.
- No decir que la GUI funciona completamente hasta probar sus CRUD y reportes.
- No decir que una captura demuestra un RF si no corresponde a una acción real.
- No marcar una tarea o prueba como completada si falta validación o evidencia.
